    # Deploy Checklist (GitHub + Streamlit Community Cloud)

## 1) Local sanity check

```bash
cd "/mnt/c/Users/juand/GitHub Projects/drake_hello"
source .venv_wsl/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Verify:
- App loads locally.
- No import errors.
- Main dashboard renders and runs benchmark.

---

## 2) GitHub repo (clean)

From `drake_hello` root:

```powershell
git init
git add .
git commit -m "Initial Streamlit deploy-ready commit"
git branch -M main
git remote add origin https://github.com/<your-user>/drake_hello.git
git push -u origin main
```

Verify in GitHub:
- `README.md` exists.
- `requirements.txt` exists.
- `runtime.txt` exists.
- `streamlit_app.py` exists.

---

## 3) Streamlit Community Cloud setup

In Streamlit Cloud > **New app**:
- Repository: `drake_hello`
- Branch: `main`
- Main file path: `streamlit_app.py`

Click **Deploy**.

---

## 4) If deployment fails

Check build logs for:
- Python version mismatch -> ensure `runtime.txt` is committed.
- Missing dependency -> update `requirements.txt`.
- Wrong entrypoint -> ensure `streamlit_app.py`.

Redeploy after push:

```powershell
git add .
git commit -m "Fix deploy issue"
git push
```

---

## 5) Final QA for application link

On `*.streamlit.app` verify:
- App opens in normal browser session.
- Benchmark runs (adaptive vs baseline).
- Metrics table and plots render.
- No crash after interaction.

