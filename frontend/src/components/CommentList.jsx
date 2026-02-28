export default function CommentList({ comments }) {
  if (!comments?.length) return <p className="comments-empty">No comments yet.</p>
  return (
    <ul className="comment-list">
      {comments.map((c, i) => (
        <li key={i} className="comment-item">
          <span className="comment-persona">{c.persona}</span>
          <span className="comment-text">{c.text}</span>
        </li>
      ))}
    </ul>
  )
}
