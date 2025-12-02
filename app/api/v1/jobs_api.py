from fastapi import APIRouter, UploadFile, File, Form, Body  # Added Body import
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
import pandas as pd
from io import BytesIO
import uuid
from datetime import datetime

# Initialize router (matches your project's modular structure)
router = APIRouter(tags=["ECS Batch Creation"])

# ------------------------------
# Data Models (Pydantic Validation)
# ------------------------------
class ECSInstanceConfig(BaseModel):
    """Schema for single ECS instance configuration (from JSON/parsed file)"""
    instance_name: str = Field(..., description="ECS instance name (unique)")
    instance_type: str = Field(..., description="ECS instance type (e.g., t3.medium, c5.large)")
    region: str = Field(..., description="AWS region (e.g., us-east-1, eu-west-1)")
    image_id: str = Field(..., description="AMI ID (e.g., ami-0c55b159cbfafe1f0)")
    subnet_id: str = Field(..., description="Subnet ID (e.g., subnet-0123456789abcdef0)")
    security_group_ids: List[str] = Field(..., description="List of security group IDs")
    key_name: Optional[str] = Field(None, description="SSH key pair name (optional)")
    tags: Optional[Dict[str, str]] = Field(None, description="Custom tags (optional)")
    login_password: Optional[str] = Field(None, description="Login password for the instance (optional)")

    # Fix: Add check for regex module (v.match() requires a compiled regex or string pattern)
    @validator("region")
    def validate_region_format(cls, v):
        import re  # Import regex module (critical fix)
        pattern = re.compile(r"^[a-z]{2}-[a-z]+-\d$")  # Compile regex pattern
        if not pattern.match(v):
            raise ValueError("Invalid region format (e.g., cn-north-1)")
        return v

class BatchECSCreateRequest(BaseModel):
    """Request model for JSON-based batch ECS creation"""
    instances: List[ECSInstanceConfig] = Field(..., description="List of ECS instances to create")
    dry_run: bool = Field(False, description="Dry run (validate only, no actual creation)")
    batch_id: Optional[str] = Field(None, description="Custom batch ID (auto-generated if not provided)")

# ------------------------------
# Utility Functions
# ------------------------------
def generate_batch_id() -> str:
    """Generate unique batch ID for tracking"""
    return f"ecs-batch-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def parse_ecs_file(file_data: bytes, file_type: str) -> List[Dict]:
    """Parse CSV/Excel file into list of ECS configs (matches ECSInstanceConfig schema)"""
    try:
        # Read file with pandas (dtype=str to avoid type conversion errors)
        if file_type == "csv":
            df = pd.read_csv(BytesIO(file_data), dtype=str, skip_blank_lines=True)
        elif file_type in ["xlsx", "xls"]:
            df = pd.read_excel(BytesIO(file_data), dtype=str, skip_blank_lines=True)
        else:
            raise ValueError(f"Unsupported file type: {file_type} (only csv/xlsx/xls allowed)")

        # Clean data: remove empty rows/columns, strip whitespace from headers
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df.columns = [col.strip() for col in df.columns]

        # Convert security_group_ids from string (e.g., "sg-1,sg-2") to list
        if "security_group_ids" in df.columns:
            df["security_group_ids"] = df["security_group_ids"].apply(
                lambda x: [sg.strip() for sg in x.split(",")] if pd.notna(x) else []
            )

        # Convert tags from string (e.g., "env:prod,name:web") to dict
        if "tags" in df.columns:
            df["tags"] = df["tags"].apply(
                lambda x: dict([tag.strip().split(":") for tag in x.split(",")]) if pd.notna(x) else None
            )

        # Convert DataFrame to list of dicts (matches ECSInstanceConfig)
        return df.to_dict("records")
    except Exception as e:
        raise ValueError(f"File parsing failed: {str(e)}")

# ------------------------------
# Core Endpoint (Fixed JSON + File Upload Support)
# ------------------------------

# ------------------------------
# Endpoint 1: JSON-based Batch Creation
# ------------------------------
@router.post("/ecs_creation/json", summary="Batch create ECS instances (JSON input)")
async def batch_create_ecs_json(
    json_request: BatchECSCreateRequest  # Required (no Optional[None])
):
    final_batch_id = json_request.batch_id or generate_batch_id()
    ecs_configs = [config.dict() for config in json_request.instances]
    
    try:
        validated_instances = [ECSInstanceConfig(**config) for config in ecs_configs]
        instance_count = len(validated_instances)
        
        if json_request.dry_run:
            return {
                "status": "dry_run_completed",
                "batch_id": final_batch_id,
                "message": f"Successfully validated {instance_count} ECS configs",
                "validated_instances": [inst.dict() for inst in validated_instances]
            }
        
        # Add ECS creation logic here
        return {
            "status": "batch_creation_initiated",
            "batch_id": final_batch_id,
            "message": f"Started creating {instance_count} ECS instances"
        }
    except Exception as e:
        return {"error": str(e), "batch_id": final_batch_id}

# ------------------------------
# ------------------------------
# Endpoint 2: File-based Batch Creation (CSV/Excel)
# ------------------------------
@router.post("/ecs_creation/file", summary="Batch create ECS instances (File upload)")
async def batch_create_ecs_file(
    file: UploadFile = File(..., description="CSV/Excel file with ECS configs"),
    # 👇 Change dry_run to Optional[str] (accept "true"/"false" as text)
    dry_run: Optional[str] = Form("false", description="Dry run (validate only: 'true' or 'false')"),
    batch_id: Optional[str] = Form(None, description="Custom batch ID")
):
    final_batch_id = batch_id or generate_batch_id()
    file_ext = file.filename.split(".")[-1].lower()
    
    # Validate file type
    if file_ext not in ["csv", "xlsx", "xls"]:
        return {"error": f"Unsupported file type: {file_ext}. Allowed: csv, xlsx, xls", "batch_id": final_batch_id}
    
    # 👇 Convert dry_run string to boolean (handle case-insensitive + whitespace)
    try:
        # Clean input: lowercase + remove whitespace
        dry_run_clean = dry_run.strip().lower()
        if dry_run_clean not in ["true", "false"]:
            raise ValueError(f"Invalid dry_run value: {dry_run}. Use 'true' or 'false'")
        final_dry_run = dry_run_clean == "true"
    except Exception as e:
        return {"error": str(e), "batch_id": final_batch_id}
    
    try:
        # Read and parse file
        file_data = await file.read()
        ecs_configs = parse_ecs_file(file_data, file_ext)
        
        # Validate ECS configs
        validated_instances = [ECSInstanceConfig(**config) for config in ecs_configs]
        instance_count = len(validated_instances)
        
        # Dry run logic
        if final_dry_run:
            return {
                "status": "dry_run_completed",
                "batch_id": final_batch_id,
                "message": f"Successfully validated {instance_count} ECS configs (no instances created)",
                "validated_instances": [inst.dict() for inst in validated_instances]
            }
        
        # Actual ECS creation logic (add your boto3 code here)
        return {
            "status": "batch_creation_initiated",
            "batch_id": final_batch_id,
            "message": f"Started creating {instance_count} ECS instances",
            "instance_count": instance_count,
            "created_instances": [inst.dict() for inst in validated_instances],
            "tracking_url": f"/api/v1/jobs/{final_batch_id}"
        }
    except ValueError as e:
        return {"error": f"Validation/parsing failed: {str(e)}", "batch_id": final_batch_id}
    except Exception as e:
        return {"error": f"Batch creation failed: {str(e)}", "batch_id": final_batch_id}
