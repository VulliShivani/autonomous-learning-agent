from dataclasses import dataclass

@dataclass
class Checkpoint:
    topic: str
    
TOPICS = {
    "Python": [
        "Introduction to Python",
        "Variables and Data Types",
        "Operators",
        "Conditional Statements",
        "Loops",
        "Functions",
        "Lists and Tuples",
        "Dictionaries and Sets",
        "File Handling",
        "OOP in Python"
    ],

    "Data Structures": [
        "Arrays",
        "Linked List",
        "Stack",
        "Queue",
        "Recursion",
        "Hashing",
        "Trees",
        "Binary Search Tree",
        "Graphs",
        "Heap"
    ],

    "Machine Learning": [
        "What is ML?",
        "Supervised Learning",
        "Unsupervised Learning",
        "Regression",
        "Classification",
        "KNN",
        "Decision Trees",
        "SVM",
        "Clustering",
        "Model Evaluation"
    ],

    "Web Development": [
        "HTML Basics",
        "CSS Basics",
        "JavaScript Basics",
        "DOM",
        "APIs",
        "React Intro",
        "NodeJS",
        "Express",
        "Databases",
        "Deployment"
    ],

    "SQL": [
        "Introduction to SQL",
        "SELECT",
        "WHERE",
        "JOINS",
        "GROUP BY",
        "HAVING",
        "Subqueries",
        "Indexes",
        "Transactions",
        "Optimization"
    ],

    "Operating Systems": [
        "Introduction to OS",
        "Processes",
        "Threads",
        "CPU Scheduling",
        "Deadlock",
        "Memory Management",
        "Virtual Memory",
        "Paging",
        "File Systems",
        "Synchronization"
    ],

    "Computer Networks": [
        "OSI Model",
        "TCP/IP",
        "IP Addressing",
        "Subnetting",
        "DNS",
        "HTTP/HTTPS",
        "Routing",
        "Switching",
        "Network Security",
        "Firewalls"
    ],

    "Artificial Intelligence": [
        "What is AI?",
        "Search Algorithms",
        "Game Theory",
        "Knowledge Representation",
        "Expert Systems",
        "Neural Networks",
        "Deep Learning",
        "NLP",
        "Computer Vision",
        "Ethics in AI"
    ],

    "Cloud Computing": [
        "What is Cloud?",
        "IaaS",
        "PaaS",
        "SaaS",
        "AWS Basics",
        "Azure Basics",
        "Google Cloud",
        "Containers",
        "Kubernetes",
        "Serverless"
    ],

    "Cyber Security": [
        "Introduction to Security",
        "Cryptography",
        "Symmetric Encryption",
        "Asymmetric Encryption",
        "Hashing",
        "Malware",
        "Phishing",
        "Firewalls",
        "Penetration Testing",
        "Ethical Hacking"
    ]
}
