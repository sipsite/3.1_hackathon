import { Link } from 'react-router-dom'

export default function PaperCard({ paper }) {
  const content = paper.brief || paper.title?.slice(0, 80) || 'No title'
  const posterUrl = paper.poster_url || 'https://via.placeholder.com/300x400?text=Paper'
  return (
    <Link to={`/paper/${paper.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <article className="paper-card">
        <div className="paper-card-cover">
          <img src={posterUrl} alt="" />
        </div>
        <p className="paper-card-brief">{content}</p>
        <div className="paper-card-meta">
          <span>♥ 0</span>
          <span>💬 {paper.comments?.length ?? 0}</span>
        </div>
      </article>
    </Link>
  )
}
