from llm import get_llm
from structured_mode import run_structured_mode
from free_mode import run_free_mode
from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

def main():
    llm = get_llm()

    print("Choose Learning Mode:")
    print("1. Structured Checkpoint Learning")
    print("2. Learn Any Topic (Free Mode)")

    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        run_structured_mode(llm)
    elif choice == "2":
        topic = input("Enter topic: ")
        run_free_mode(llm, topic)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
