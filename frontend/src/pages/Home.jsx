import { useState, useEffect } from 'react'
import { getPapers } from '../api/client'
import PaperCard from '../components/PaperCard'

export default function Home() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getPapers()
      .then((d) => setPapers(d.papers || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (error) return <div className="page">Error: {error}</div>
  if (loading) return <div className="page">Loading...</div>

  const left = papers.filter((_, i) => i % 2 === 0)
  const right = papers.filter((_, i) => i % 2 === 1)

  return (
    <div className="page home">
      <header className="header">
        <h1 className="logo">PaperDaily</h1>
      </header>
      <main className="feed">
        <div className="feed-col">
          {left.map((p) => (
            <PaperCard key={p.id} paper={p} />
          ))}
        </div>
        <div className="feed-col">
          {right.map((p) => (
            <PaperCard key={p.id} paper={p} />
          ))}
        </div>
      </main>
    </div>
  )
}
