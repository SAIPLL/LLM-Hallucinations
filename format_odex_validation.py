import json
import os

def from_odex_to_validator(model):
    folder_path = f"Data/odex/data/nl2code/{model}"
    data_validation = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith("0.json"):
            # Construct the full file path
            file_path = os.path.join(folder_path, file_name)
            # Open and read the JSON file
            with open(file_path, 'r') as file:
                data_answers = json.load(file)
            # Open and read the test 
            lang = file_name[:2]
            test_path = f"Data/odex/data/{lang}_test.jsonl"
            i = 0
            with open(test_path, 'r') as test_file:
                for line in test_file:
                    # Load each line as a JSON object
                    task_info = json.loads(line.strip())
                    if "import " not in task_info["test_start"]:
                      continue
                    # Get passed and results from data_answers
                    key_test = "output"
                    if "outputs" in data_answers[i]:
                        key_test = "outputs"
                    data_validator = {
                        "id" : task_info["task_id"],
                        "lang" : lang,
                        "code" : data_answers[i]["predictions"],
                        "passed" : data_answers[i][key_test][0][1]["passed"],
                        "result" : data_answers[i][key_test][0][1]["result"],
                        "metadata" : task_info
                    }
                    data_validation.append(data_validator)
                    i = i + 1
            # Save answers in format
    # Filename to write answers on
    output_name = f"Data/odex/data/nl2code/{model}/{model}-0-answers.jsonl"
    with open(output_name, "w") as file_write:
        for entry in data_validation:
            file_write.write(json.dumps(entry) + "\n")

def main():
	from_odex_to_validator("claude-3-opus-20240229")
	from_odex_to_validator("gpt-3.5-turbo-0125")
	from_odex_to_validator("gpt-4-0613")
	from_odex_to_validator("granite-code-latest")

if __name__ == "__main__":
	main()