import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import axios from 'axios';
import '../App.css';

// const dummyData = [
//   {
//     id: 1,
//     name: "나라뜌",
//     title: "과자를 먹었다",
//     content: "맛있었습니다. 내일 또 사먹어야지.",
//     date: "2026-04-13 14:30"
//   },
//   {
//     id: 2,
//     name: "수아뜌",
//     title: "친구와의 카페 만남",
//     content: "아메리카노를 마시며 오랜만에 많은 이야기를 나누어 즐거웠다.",
//     date: "2026-04-12 18:00"
//   },
//   {
//     id: 3,
//     name: "윤주뜌",
//     title: "아침 운동",
//     content: "가볍게 3km를 달렸다. 공기가 상쾌하다.",
//     date: "2026-04-11 07:00"
//   },
//   {
//     id: 4,
//     name: "가영뜌",
//     title: "노래방",
//     content: "3시간동안 노래불렀다. 목이 아프다.",
//     date: "2026-04-10 09:00"
//   }
// ];


const TimelinePage = () => {
  const [diaries, setDiaries] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchDiaries = async () => {
      try {
        const response = await axios.get('http://localhost:8000/diaries')
        setDiaries(response.data)
      } catch (error) {
        console.error('목록 로딩 에러 : ', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDiaries()
  }, [])

  const handleCardClick = (item) => {
    navigate(`/post/${item.id}`, { state: { post: item } });
  };

  if (isLoading) return <div className="loading">로딩 중...</div>

  return (
    <div className="animate-fade-in">
      <h2 className="section-title">타임라인</h2>
      <div className="timeline-feed">
        {
          diaries.length > 0 ? (
            diaries.map((item, index) => (
              <div
                key={item.id}
                className="timeline-card"
                style={{ animationDelay: `${index * 0.1}s`, cursor: 'pointer' }}
                onClick={() => handleCardClick(item)}
              >
                <div className="card-header">
                  <div className="card-avatar">{item.name.charAt(0)}</div>
                  <div className="card-meta">
                    <span className="card-author">{item.name}</span>
                  </div>
                  <div className="card-id-badge">
                    #{item.id}
                  </div>
                </div>
                <div className="card-body">
                  <h3 className="card-title">{item.title}</h3>
                  <p className="card-content">{item.content}</p>
                </div>
                <div className="card-footer">
                  {item.regDate || item.date}
                </div>
              </div>
            ))
          ) : (
            <div className="no-data">
              <p>아직 작성된 일기가 없습니다.</p>
            </div>
          )
        }
      </div>
    </div>
  );
};

export default TimelinePage;
