modules = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'python-multipart': 'multipart',
    'bcrypt': 'bcrypt',
    'python-jose': 'jose',
    'pydantic': 'pydantic',
    'pydantic-settings': 'pydantic_settings',
    'sqlalchemy': 'sqlalchemy',
    'python-dotenv': 'dotenv',
    'PyPDF2': 'PyPDF2',
    'python-docx': 'docx',
    'pillow': 'PIL',
    'langchain': 'langchain',
    'openai': 'openai',
    'sentence-transformers': 'sentence_transformers',
    'faiss-cpu': 'faiss',
    'numpy': 'numpy',
    'scikit-learn': 'sklearn',
    'nltk': 'nltk',
    'textstat': 'textstat',
    'deep-translator': 'deep_translator',
    'reportlab': 'reportlab',
    'requests': 'requests',
    'aiofiles': 'aiofiles',
    'cryptography': 'cryptography',
    'passlib': 'passlib',
    'pytest': 'pytest',
    'pytest-asyncio': 'pytest_asyncio',
    'httpx': 'httpx'
}

import importlib, sys

results = {}
for pkg, mod in modules.items():
    try:
        importlib.import_module(mod)
        results[pkg] = True
    except Exception as e:
        results[pkg] = False

print('IMPORT_CHECK_RESULTS')
for pkg, ok in results.items():
    print(f"{pkg}: {'OK' if ok else 'MISSING'}")

# Exit code 0 even if missing; caller can parse output
