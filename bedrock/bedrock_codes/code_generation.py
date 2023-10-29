import json
import boto3
import json
from datetime import datetime

def generate_code_for_prompt(event, context):
    try:
        event = json.loads(event['body'])
        message = event['message']
        language = event['language']
        prompt_text = f"""Human: Write {language} code for the following instructions: {message}.
        Assistant:
        """
        body = {
            "prompt": prompt_text,
            "max_tokens_to_sample": 2048,
            "temperature": 0.1,
            "top_k":250,
            "top_p": 0.2,
            "stop_sequences":["\n\nHuman:"]
        }

        bedrock = boto3.client("bedrock-runtime",region_name="us-west-2")
        response = bedrock.invoke_model(body=json.dumps(body),modelId="anthropic.claude-v2")
        response_content = response.get('body').read().decode('utf-8')
        response_data = json.loads(response_content)
        code = response_data["completion"].strip()

        s3 = boto3.client('s3')
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f'code-output/{current_time}.txt'
        s3_bucket = 'bedrock-output-bucket'
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = code)
        print("Code generation completed and saved to s3")

        return {
            'statusCode':200,
            'body':json.dumps('Code generation completed')
        }
    except Exception as e:
        print("Error while generating code using Bedrock:", str(e))
        return {
            'statusCode':500,
            'body':json.dumps(f'Code generation failed: {str(e)}')
        }