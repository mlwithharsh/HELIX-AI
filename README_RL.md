# RL Fine-Tuning Pipeline

## Project structure

```text
/model
/rl
/memory
/tests
/docker
train_rl.py
evaluate_rl.py
requirements-rl.txt
```

## Install

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-rl.txt
```

## Train

```powershell
python train_rl.py --model-name distilgpt2 --epochs 1 --log-dir logs
```

## Test

```powershell
pytest tests -q
```

## Evaluate

```powershell
python evaluate_rl.py --log-dir logs
```

## Docker

```powershell
docker build -f docker/Dockerfile -t echo-rl .
docker run --rm -it -v ${PWD}\logs:/app/logs echo-rl
```
