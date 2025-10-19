from src.db import build_single_document_index, build_index
from src.file_manager_agent import app, system_prompt
from langchain_core.messages import HumanMessage


def main():
    # while 1:
        # build_index(root_path="D:/", max_folders=None)
        
    messages = [system_prompt]
    while 1:
        request = input("User: ")
        result = app.invoke({"messages": messages + [HumanMessage(request)]}, config={"recursion_limit": 25})
        print(result["messages"][-1].content)
        messages = result["messages"]

if __name__ == "__main__":
    main()
