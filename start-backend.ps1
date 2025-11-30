Start-Process -NoNewWindow mosquitto
Start-Sleep -Seconds 2
Start-Process -FilePath "uvicorn" -ArgumentList "main:app --port 8000 --reload" -WorkingDirectory "Backend/agents/orchestrator"
Start-Process -FilePath "uvicorn" -ArgumentList "main:app --port 8011 --reload" -WorkingDirectory "Backend/agents/planner"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/maint"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/energy"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/cyber"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/safety"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/ppe"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/publisher"