import json
from typing import Dict, Any, List, Optional
import os

def load_openapi_spec(file_path: str) -> Dict[str, Any]:
    """
    Load the OpenAPI specification from a JSON file.
    
    Args:
        file_path: Path to the OpenAPI JSON file.
        
    Returns:
        Dict[str, Any]: The parsed OpenAPI specification.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_operation_details(spec: Dict[str, Any], operation_id: str) -> Optional[Dict[str, Any]]:
    """
    Extract details for a specific operation from the OpenAPI spec.
    
    Args:
        spec: The OpenAPI specification.
        operation_id: The operation ID to extract.
        
    Returns:
        Optional[Dict[str, Any]]: The operation details if found, None otherwise.
    """
    # Iterate through all paths and methods to find the operation
    for path, path_item in spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch'] and operation.get('operationId') == operation_id:
                return {
                    'path': path,
                    'method': method,
                    'operation': operation,
                    'parameters': operation.get('parameters', []),
                    'responses': operation.get('responses', {}),
                    'requestBody': operation.get('requestBody', None)
                }
    return None

def create_tool_schema(operation_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a schema for an MCP tool based on operation details.
    
    Args:
        operation_details: The details of the operation.
        
    Returns:
        Dict[str, Any]: The schema for the MCP tool.
    """
    parameters = {}
    
    # Add path parameters
    for param in operation_details.get('parameters', []):
        if param.get('in') == 'path':
            param_name = param.get('name')
            param_schema = param.get('schema', {})
            parameters[param_name] = {
                'type': param_schema.get('type', 'string'),
                'description': param.get('description', ''),
                'required': param.get('required', False)
            }
    
    # Add query parameters
    for param in operation_details.get('parameters', []):
        if param.get('in') == 'query':
            param_name = param.get('name')
            param_schema = param.get('schema', {})
            parameters[param_name] = {
                'type': param_schema.get('type', 'string'),
                'description': param.get('description', ''),
                'required': param.get('required', False)
            }
    
    return {
        'name': f"voltage://{operation_details['operation']['operationId']}",
        'description': operation_details['operation'].get('description', 
                       operation_details['operation'].get('summary', 
                       f"Execute {operation_details['operation']['operationId']}")),
        'parameters': parameters
    }
