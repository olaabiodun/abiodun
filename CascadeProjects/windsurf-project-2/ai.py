"""
  pip i bytez
"""

from bytez import Bytez

sdk = Bytez("453fa58aaee044bcec2661e90dc98324")

# choose gpt-4o-mini
model = sdk.model("openai/gpt-4o-mini")

# send input to model
response = model.run([
  {
    "role": "user",
    "content": "Hello"
  }
])

# Print the full response to inspect its structure
print("Full response:", response)

# Try to extract output and error if they exist in the response
# The exact structure depends on what model.run() returns
try:
    if isinstance(response, (list, tuple)):
        if len(response) >= 2:
            output, error = response[0], response[1]
            print({"error": error, "output": output})
        else:
            print({"response": response})
    else:
        print({"response": response})
except Exception as e:
    print({"error": str(e), "response": response})