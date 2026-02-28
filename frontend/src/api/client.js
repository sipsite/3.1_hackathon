const API_BASE = '/api'

export async function getPapers(params = {}) {
  const q = new URLSearchParams(params).toString()
  const res = await fetch(`${API_BASE}/papers${q ? `?${q}` : ''}`)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getPaper(id) {
  const res = await fetch(`${API_BASE}/papers/${id}`)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getComments(paperId) {
  const res = await fetch(`${API_BASE}/papers/${paperId}/comments`)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function postChat(paperId, messages) {
  const res = await fetch(`${API_BASE}/papers/${paperId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}
