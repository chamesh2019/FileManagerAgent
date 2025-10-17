from src.db import build_single_document_index
from src.file_manager_agent import app
from langchain_core.messages import HumanMessage


def main():
    # build_single_document_index(root_path="D:/", additional_paths=["C:/Users/chame/Downloads"])
    messages = []
    while 1:
        request = input("User: ")
        result = app.invoke({"messages": messages + [HumanMessage(request)]}, config={"recursion_limit": 25})
        print(result["messages"][-1].content)
        messages = result["messages"]

if __name__ == "__main__":
    main()
