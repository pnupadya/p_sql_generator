import os
from llama_cpp import Llama

# --- Define paths to your SQL Schema Files ---
SQL_SCHEMA_DIR = "/Users/pnupadya/Documents/learn/git_repos/sql_generator/sql/"
EMPLOYEE_SCHEMA_FILE = os.path.join(SQL_SCHEMA_DIR, "employee.sql")
DEPARTMENT_SCHEMA_FILE = os.path.join(SQL_SCHEMA_DIR, "department.sql")

def load_schema_from_file(filepath: str) -> str:
    """Loads SQL schema from a specified file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Schema file not found at {filepath}")
        print("Please ensure you have created the 'sql_generator/sql/' directory and placed 'employee.sql' and 'department.sql' inside it.")
        exit(1)
    except Exception as e:
        print(f"Error reading schema file {filepath}: {e}")
        exit(1)

# Load schemas
EMPLOYEE_SCHEMA = load_schema_from_file(EMPLOYEE_SCHEMA_FILE)
DEPARTMENT_SCHEMA = load_schema_from_file(DEPARTMENT_SCHEMA_FILE)

# Combine schemas for the LLM's context
DATABASE_SCHEMA = f"### employee table schema:\n{EMPLOYEE_SCHEMA}\n\n### department table schema:\n{DEPARTMENT_SCHEMA}"


# --- Model Initialization ---
# Adjust this path to match where you saved your .gguf file
MODEL_PATH = "/Users/pnupadya/Documents/learn/models/deepseek/ds_coder/deepseek-coder-1.3b-instruct.Q3_K_M.gguf" # IMPORTANT: Update this if your file name differs

# Number of CPU threads to use. Adjust based on your MacBook Air's cores.
# A good starting point is half your physical cores or fewer for general use.
# (e.g., M1/M2 Air typically have 4 performance + 4 efficiency cores).
N_THREADS = 4
# Max context length for the model. 4096 is common for DeepSeek-Coder.
N_CTX = 512 #4096

print(f"Loading LLM model from: {MODEL_PATH}")
print(f"Using {N_THREADS} CPU threads and context length {N_CTX}.")

try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_gpu_layers=-1 if os.uname().sysname == 'Darwin' and os.uname().machine.startswith('arm') else 0,
        # -1 means all layers offloaded to GPU if METAL is enabled, 0 means no layers offloaded.
        # Only set n_gpu_layers > 0 if you installed with METAL support and have Apple Silicon.
        verbose=True # Set to False for less verbose output during inference
    )
except Exception as e:
    print(f"Error initializing Llama model: {e}")
    print(f"Please ensure '{MODEL_PATH}' exists and is a valid GGUF file.")
    print("Also verify `llama-cpp-python` was installed correctly, especially with METAL support if on Apple Silicon.")
    exit(1)

# --- Prompt Engineering ---
# This structure guides the DeepSeek model to generate SQL.
# We follow the DeepSeek-Coder instruct format for chat.
def format_prompt(natural_language_query: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant that translates natural language questions into SQL queries. Provide only the SQL query, enclosed in markdown code blocks, do not provide any additional text or explanation. Use the provided database schema."},
        {"role": "user", "content": f"""
    Given the following database schema:
    {DATABASE_SCHEMA}

    Translate the following natural language query into a SQL query:
    "{natural_language_query}"

    ```sql
    """}
    ]
    return messages


# --- Main interaction loop ---
if __name__ == "__main__":
    print("\n--- SQL Query Generator (Powered by DeepSeek-Coder-1.3B-Instruct via llama.cpp) ---")
    print("Enter your natural language query, or type 'exit' to quit.")

    while True:
        user_input = input("\nYour prompt: ")
        if user_input.lower() == 'exit':
            break

        messages = format_prompt(user_input)

        try:
            print("Generating SQL query...")
            # Use create_chat_completion for structured chat input
            response = llm.create_chat_completion(
                messages=messages,
                temperature=0.1,  # Lower temperature for more deterministic/focused output
                max_tokens=256,   # Max tokens for the SQL query
                stop=["```"]      # Stop generation when it encounters the end of a code block
            )

            # Extract and print the generated SQL
            generated_text = response['choices'][0]['message']['content'].strip()

            # Clean up the output to ensure only SQL is present
            if generated_text.startswith("```sql"):
                generated_text = generated_text[len("```sql"):].strip()
            if "```" in generated_text:
                generated_text = generated_text.split("```")[0].strip()

            print("\nGenerated SQL Query:")
            print(generated_text)
            print("-" * 30)

        except Exception as e:
            print(f"An error occurred during generation: {e}")
            print("Please try again or check your model path/environment setup.")

    print("Exiting SQL Query Generator. Goodbye!")
