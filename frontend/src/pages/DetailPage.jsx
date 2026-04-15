import React from 'react';
import { useLocation, useNavigate } from 'react-router';
import '../App.css';

const DetailPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const post = location.state?.post;

  if (!post) {
    return (
      <div className="animate-fade-in">
        <h2 className="section-title">게시글을 찾을 수 없습니다.</h2>
        <button className="submit-btn" onClick={() => navigate('/timeline')}>
          목록으로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div className="animate-fade-in detail-page">
      <button
        className="back-btn"
        onClick={() => navigate(-1)}
      >
        ← 뒤로 가기
      </button>

      <div className="timeline-card detail-card">
        <div className="card-header">
          <div className="card-avatar">{post.name.charAt(0)}</div>
          <div className="card-meta">
            <span className="card-author">{post.name}</span>
          </div>
          <div className="card-id-badge">
            #{post.id}
          </div>
        </div>
        <div className="card-body">
          <h3 className="card-title">{post.title}</h3>
          <p className="card-content">{post.content}</p>
        </div>
        <div className="card-footer">
          {post.regDate || post.date}
        </div>
      </div>
    </div>
  );
};

export default DetailPage;
