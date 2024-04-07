### PDF compare test

```bash
pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### Docker build

```bash
docker build -t pdf-compare .
```

### Docker run

```bash
docker run -it --rm pdf-compare
```

### Docker run with volume

```bash
docker run -it --rm -v $(pwd):/app pdf-compare
```


http://127.0.0.1:5001/
