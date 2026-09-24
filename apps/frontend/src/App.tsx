import { useState, useEffect } from 'react';
import type { PostConnectionCustomData, Dbms, GetConnectionStatusResponse, PostConnectionQueryData, PostConnectionQueryResponse, PostConnectionQueryError } from "./client"

const PIPELINE_URL = "http://localhost:8000/pipeline";

interface APIResponse<T> {
  data: T;
  metadata: unknown | null;
}

async function connect(): Promise<string> {
  const demoURL = `${PIPELINE_URL}/connect/demo`;
  const requestOptions: RequestInit = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: "include",
  };

  const response = await fetch(demoURL, requestOptions);
  const statusCode = response.status.toString();
  const re = /^4[0-9]{2}$/;
  if (statusCode == re.exec(statusCode)?.[0]) {
    return "Error occured: " + statusCode;
  }

  return "Success";
}


async function connectCustom(): Promise<string> {
  const payload: PostConnectionCustomData = {
    body: {
      dbms: (document.getElementById("dbms") as HTMLSelectElement).value as Dbms,
      username: (document.getElementById("username") as HTMLInputElement).value,
      password: (document.getElementById("password") as HTMLInputElement).value,
      host: (document.getElementById("host") as HTMLInputElement).value,
      port: parseInt((document.getElementById("port") as HTMLInputElement).value),
      db: (document.getElementById("database") as HTMLInputElement).value,
      schema: (document.getElementById("schema") as HTMLInputElement).value
    },
    url: "/connection/custom"
  }
  const customURL = `${PIPELINE_URL}/connect/custom`;
  const body = payload.body;
  const requestOptions: RequestInit = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: "include",
    body: JSON.stringify(body)
  };

  const response = await fetch(customURL, requestOptions);
  const statusCode = response.status.toString();
  const re = /^4[0-9]{2}$/;
  if (statusCode == re.exec(statusCode)?.[0]) {
    return "Error occured: " + statusCode;
  }

  return "Success";
}


async function checkConnStatus(): Promise<GetConnectionStatusResponse> {
  const connStatusURL = `${PIPELINE_URL}/is-connected`;
  
  const response = await fetch(connStatusURL, {credentials: "include"});
  const body: APIResponse<GetConnectionStatusResponse> = await response.json();
  return body.data;
}


async function query(prompt: string): Promise<PostConnectionQueryResponse> {
  const payload: PostConnectionQueryData = {
    body: { prompt },
    url: "/connection/query"
  };
  const queryURL = `${PIPELINE_URL}/query`;
  const requestOptions: RequestInit = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload.body),
    credentials: "include",
  };

  const response = await fetch(queryURL, requestOptions);

  if (!response.ok) {
    const errorBody: PostConnectionQueryError = await response.json();
    const errorDetails = `Status code: ${response.status}\n` + JSON.stringify((errorBody.detail && response.status == 422) ? errorBody.detail[0] : errorBody.detail);
    throw new Error(errorDetails);
  }

  const body: APIResponse<PostConnectionQueryResponse> = await response.json();
  return body.data;
}


function App() {
  const [targetDB, setTargetDB] = useState("demo");
  const [status, setStatus] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [db, setDB] = useState<string | null | undefined>(null);
  const [prompt, setPrompt] = useState("");
  const [queryResult, setQueryResult] = useState<PostConnectionQueryResponse | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const checkStatus = async () => {
      const connStatus = await checkConnStatus();
      setChecking(false);
      setIsConnected(connStatus.connected);
      setDB(connStatus.database);
    };

    const timeoutId = setTimeout(checkStatus, 1000);
    return () => clearTimeout(timeoutId);
  }, []);

  const handleConnect = async () => {
    const resStatus = await connect();
    setStatus(resStatus);
    await new Promise(r => setTimeout(r, 2500));
    const connStatus = await checkConnStatus();
    setIsConnected(connStatus.connected);
    setDB(connStatus.database);
  };

  const handleConnectCustom = async () => {
    const resStatus = await connectCustom();
    setStatus(resStatus);
    await new Promise(r => setTimeout(r, 2500));
    const connStatus = await checkConnStatus();
    setIsConnected(connStatus.connected);
    setDB(connStatus.database);
  }

  const handleQuery = async () => {
    setProcessing(true);
    try {
      const res = await query(prompt);
      setProcessing(false);
      setQueryResult(res);
    } catch (err) {
      setQueryError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <div>
      <div>
        
      </div>

      <div>
        <input type="radio" name="connection" id="demo" onChange={(e) => setTargetDB(e.target.id)} defaultChecked />
        <label htmlFor="demo">Demo</label>
        <br />
        <input type="radio" name="connection" id="custom" onChange={(e) => setTargetDB(e.target.id)} />
        <label htmlFor="custom">Custom</label>
        <br />
        <form action="">
          {targetDB == "custom" &&
            <>
              <div>
                <label htmlFor="dbms">DBMS: </label>
                <select name="dbms" id="dbms">
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="mariadb">MariaDB</option>
                  <option value="sqlite">SQLite</option>
                  <option value="oracle">Oracle</option>
                  <option value="mssql">Microsoft SQL Server</option>
                </select>
              </div>
              <div>
                <label htmlFor="username">Username: </label>
                <input type="text" id='username' />
              </div>
              <div>
                <label htmlFor="password">Password: </label>
                <input type="password" id='password' />
              </div>
              <div>
                <label htmlFor="host">Host: </label>
                <input type="text" id='host' />
              </div>
              <div>
                <label htmlFor="port">Port: </label>
                <input type="text" id='port' />
              </div>
              <div>
                <label htmlFor="database">Database: </label>
                <input type="text" id='database' />
              </div>
              <div>
                <label htmlFor="schema">Schema: </label>
                <input type="text" id='schema' placeholder="Leave blank if not applicable"/>
              </div>
            </>
          }
          <button type="button" onClick={targetDB == "demo" ? handleConnect : handleConnectCustom}>Connect</button>
        </form>
        <p>{status}</p>
      </div>

      <p>Connection status: {checking ? "Checking..." : isConnected ? "Connected" : "Not connected"}</p>
      <p>Connected to: {checking ? "Checking..." : !db ? "None" : db}</p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={1}
        style={{
          width: '20rem',
          overflow: 'hidden',
          wordWrap: 'break-word',
        }}
      />
      <br />
      <button onClick={handleQuery}>Query</button>
      {processing && <p>Processing...</p>}
      {queryError && <p style={{ color: 'red', whiteSpace: "pre-line" }}>{queryError}</p>}
      {queryResult &&
        <div>
          <p>Result: {queryResult.result}</p>
          {queryResult.sql ?
            <>
              <p>SQL:</p>
              <code>
                {queryResult.sql}
              </code>
            </>
           : 
            <p>SQL: None</p>
          }
        </div>
      }
    </div>
  )
}

export default App
