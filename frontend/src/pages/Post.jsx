import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPaper } from '../api/client'
import CommentList from '../components/CommentList'
import ChatFloat from '../components/ChatFloat'

export default function Post() {
  const { id } = useParams()
  const [paper, setPaper] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getPaper(id)
      .then(setPaper)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (error) return <div className="page">Error: {error}</div>
  if (loading || !paper) return <div className="page">Loading...</div>

  const posterUrl = paper.poster_url || 'https://via.placeholder.com/600x400?text=Paper'

  return (
    <div className="page post">
      <header className="header">
        <Link to="/" className="back">← Feed</Link>
        <h1 className="logo">PaperDaily</h1>
      </header>
      <article className="post-article">
        <div className="post-cover">
          <img src={posterUrl} alt="" />
        </div>
        <h2 className="post-title">{paper.title}</h2>
        {paper.brief && <p className="post-brief">{paper.brief}</p>}
        {paper.summary && (
          <div className="post-summary">
            <h3>Summary</h3>
            <pre className="post-summary-text">{paper.summary}</pre>
          </div>
        )}
        {paper.full_summary && (
          <div className="post-summary post-full-summary">
            <h3>Full summary</h3>
            <div className="post-summary-text">{paper.full_summary}</div>
          </div>
        )}
        {paper.abstract && (
          <details className="post-abstract">
            <summary>Abstract</summary>
            <p>{paper.abstract}</p>
          </details>
        )}
        <section className="post-comments">
          <h3>Comments</h3>
          <CommentList comments={paper.comments} />
        </section>
      </article>
      <ChatFloat paperId={id} />
    </div>
  )
}
