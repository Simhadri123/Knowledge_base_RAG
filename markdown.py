from rich.console import Console
from rich.markdown import Markdown
import json

console = Console()

with open("C:\\Users\\HP\\Desktop\\hackathon\\version2\\backend\\knowledge_base\\Accelerating_Computer_Vision_Using_Model_Compression_Techniques (4)_knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)

console.rule(data["title"])

markdown = Markdown(data["content"])

console.print(markdown)