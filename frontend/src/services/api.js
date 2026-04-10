const API_BASE_URL = "http://127.0.0.1:8000/api";

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

export async function fetchDashboard() {
  return handleResponse(await fetch(`${API_BASE_URL}/dashboard`));
}

export async function fetchSKUs(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, "true");
    }
  });
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return handleResponse(await fetch(`${API_BASE_URL}/skus${suffix}`));
}

export async function fetchAgentReview({ skuId, ...filters } = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, "true");
    }
  });
  if (skuId) {
    params.set("sku_id", skuId);
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return handleResponse(await fetch(`${API_BASE_URL}/agent-review${suffix}`));
}

export async function fetchSKUDetail(skuId) {
  return handleResponse(await fetch(`${API_BASE_URL}/skus/${skuId}`));
}

export async function askSKUQuestion(skuId, question, previousResponseId) {
  return handleResponse(
    await fetch(`${API_BASE_URL}/skus/${skuId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, previous_response_id: previousResponseId ?? null }),
    }),
  );
}

export async function runSimulation(payload) {
  return handleResponse(
    await fetch(`${API_BASE_URL}/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function runAgent() {
  return handleResponse(
    await fetch(`${API_BASE_URL}/run-agent`, {
      method: "POST",
    }),
  );
}
