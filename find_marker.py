with open('app.py', 'r') as f:
    content = f.read()

idx = content.find('return {"meters": results, "total": len(results)}')
print(f'Found at position {idx}')
# Show surrounding context
start = max(0, idx - 50)
end = min(len(content), idx + 100)
print(content[start:end])