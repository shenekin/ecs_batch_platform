# Test POST /create with custom fields + bypass Celery
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "name": "my-test-ecs-002",
    "flavor_ref": "c7n.large.2",
    "image_id": "5ad8b79d-c5c5-4e94-857c-a6c70b246553", 
    "network_id": "bf022830-f69a-4eca-a40d-261a06b4d36e",
    "key_name": "abcd_ad" ,
    "security_group_id": "672d73bf-42be-4548-bf95-28e430dcb018",
  }' \
  http://localhost:8000/ecs/create?use_celery=false
  
  {
  "server": {
    "name": "my-test-ecs-002",
    "flavorRef": "c7n.large.2",
    "imageRef": "5ad8b79d-c5c5-4e94-857c-a6c70b246553",
    "key_name": "abcd_ad",
    "networks": [{"uuid": "your-network-id"}],
    "security_groups": [{"name": "your-security-group-id"}]
  }
}

# Replace these values!
API_KEY="api-key-test"
USERNAME="admin"
PASSWORD="1qaz@WSX"
API_URL="http://localhost:8080/api/v1"

# One-liner: Get JWT → Test protected endpoint
JWT_TOKEN=$(curl -s -X POST "${API_URL}/auth/token" -H "X-API-Key: ${API_KEY}" -F "username=${USERNAME}" -F "password=${PASSWORD}" | jq -r .access_token) && \
curl -X POST "${API_URL}/jobs/ecs_creation/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "dry_run": true,
    "instances": [{"instance_name": "test-server-01", "instance_type": "t3.medium", "region": "us-east-1", "image_id": "ami-0c55b159cbfafe1f0", "subnet_id": "subnet-0123456789abcdef0", "security_group_ids": ["sg-0123456789abcdef0"]}]
  }'



curl -X POST http://localhost:8080/api/v1/auth/token \
-H "X-API-Key:api-testing" \
-F "username=admin" \
-F "password=1qaz@WSX"



curl -X POST "${API_URL}/auth/token" -H "Authorization: Bearer ${JWT_TOKEN}"

curl -X POST http://localhost:8080/api/v1/tokenjwt -H "Authorization: Bearer ${JWT_TOKEN}"
