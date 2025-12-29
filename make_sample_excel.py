import pandas as pd
import random

data = {
    'code': [f'BATCH-{i:03d}' for i in range(1, 6)],
    'name': [f'Batch Product {i}' for i in range(1, 6)],
    'category': [random.choice(['電子產品', '辦公用品']) for i in range(1, 6)],
    'spec': [f'Spec {i}' for i in range(1, 6)],
    'description': [f'Desc {i}' for i in range(1, 6)],
    'image_path': [''] * 5
}

df = pd.DataFrame(data)
df.to_excel('m:/PDM/sample_upload.xlsx', index=False)
print("Sample Excel created at m:/PDM/sample_upload.xlsx")
