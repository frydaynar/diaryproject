import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import axios from 'axios';
import '../App.css';

const InputPage = () => {
  const [diaryText, setDiaryText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!diaryText.trim()) return;

    setIsSubmitting(true);

    try {
      // 백엔드 API 호출 : 에이전트에게 일기 분석 및 저장 요청
      const response = await axios.post('http://aiedu.tplinkdns.com:6041/chat', {
        input: diaryText
      })

      if (response.data.status === 'success') {
        setDiaryText('')
        navigate('/timeline')
      }
    } catch (error) {
      console.error('에러 발생 :', error)
      alert('😥 일기 저장 중 오류가 발생했습니다 😥')
    } finally {
      setIsSubmitting(false)
    }
    // setTimeout(() => {
    //   console.log('Sending to AI Agent:', diaryText);
    //   setIsSubmitting(false);
    //   setDiaryText('');
    //   navigate('/timeline');
    // }, 1000);
  };

  return (
    <div className="animate-fade-in">
      <h2 className="section-title">일기 작성</h2>
      <p className="subtitle">어떤 일이 있었는지 자유롭게 적어주세요. AI가 깔끔하게 정리해 드립니다.</p>

      <form className="diary-form" onSubmit={handleSubmit}>
        <div className="textarea-wrapper">
          <textarea
            className="diary-textarea"
            placeholder="예시: 나는 '나라'야. 오늘 점심에 도인이랑 파스타를 먹었는데 정말 맛있었어!"
            value={diaryText}
            onChange={(e) => setDiaryText(e.target.value)}
            disabled={isSubmitting}
            rows="8"
          ></textarea>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="submit-btn"
            disabled={isSubmitting || !diaryText.trim()}
          >
            {isSubmitting ? 'AI가 정리 중...' : '기록하기'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InputPage;
