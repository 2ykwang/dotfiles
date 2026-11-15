---
paths:
  - "**/*.py"
---

# Python 코드 간격

논리적인 처리 단위 사이에 빈 줄 한 줄을 둔다. 조건부 후처리와 최종 반환은 구분하되, 모든 `return` 앞에 기계적으로 빈 줄을 넣지 않는다.

```python
def create_record(data, publish=False):
    record = save_record(data)

    if publish:
        publish_record(record)

    return record
```

```python
def find_record(records, record_id):
    for record in records:
        if record.id == record_id:
            return record

    return None
```
