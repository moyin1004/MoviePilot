import time

from sqlalchemy import Column, Integer, String, Sequence, Boolean, func
from sqlalchemy.orm import Session

from app.db.models import Base, db_persist


class TransferHistory(Base):
    """
    转移历史记录
    """
    id = Column(Integer, Sequence('id'), primary_key=True, index=True)
    # 源目录
    src = Column(String, index=True)
    # 目标目录
    dest = Column(String)
    # 转移模式 move/copy/link...
    mode = Column(String)
    # 类型 电影/电视剧
    type = Column(String)
    # 二级分类
    category = Column(String)
    # 标题
    title = Column(String, index=True)
    # 年份
    year = Column(String)
    tmdbid = Column(Integer, index=True)
    imdbid = Column(String)
    tvdbid = Column(Integer)
    doubanid = Column(String)
    # Sxx
    seasons = Column(String)
    # Exx
    episodes = Column(String)
    # 海报
    image = Column(String)
    # 下载器hash
    download_hash = Column(String, index=True)
    # 转移成功状态
    status = Column(Boolean(), default=True)
    # 转移失败信息
    errmsg = Column(String)
    # 时间
    date = Column(String, index=True)
    # 文件清单，以JSON存储
    files = Column(String)

    @staticmethod
    def list_by_title(db: Session, title: str, page: int = 1, count: int = 30):
        return db.query(TransferHistory).filter(TransferHistory.title.like(f'%{title}%')).order_by(
            TransferHistory.date.desc()).offset((page - 1) * count).limit(
            count).all()

    @staticmethod
    def list_by_page(db: Session, page: int = 1, count: int = 30):
        return db.query(TransferHistory).order_by(TransferHistory.date.desc()).offset((page - 1) * count).limit(
            count).all()

    @staticmethod
    def get_by_hash(db: Session, download_hash: str):
        return db.query(TransferHistory).filter(TransferHistory.download_hash == download_hash).first()

    @staticmethod
    def get_by_src(db: Session, src: str):
        return db.query(TransferHistory).filter(TransferHistory.src == src).first()

    @staticmethod
    def list_by_hash(db: Session, download_hash: str):
        return db.query(TransferHistory).filter(TransferHistory.download_hash == download_hash).all()

    @staticmethod
    def statistic(db: Session, days: int = 7):
        """
        统计最近days天的下载历史数量，按日期分组返回每日数量
        """
        sub_query = db.query(func.substr(TransferHistory.date, 1, 10).label('date'),
                             TransferHistory.id.label('id')).filter(
            TransferHistory.date >= time.strftime("%Y-%m-%d %H:%M:%S",
                                                  time.localtime(time.time() - 86400 * days))).subquery()
        return db.query(sub_query.c.date, func.count(sub_query.c.id)).group_by(sub_query.c.date).all()

    @staticmethod
    def count(db: Session):
        return db.query(func.count(TransferHistory.id)).first()[0]

    @staticmethod
    def count_by_title(db: Session, title: str):
        return db.query(func.count(TransferHistory.id)).filter(TransferHistory.title.like(f'%{title}%')).first()[0]

    @staticmethod
    def list_by(db: Session, mtype: str = None, title: str = None, year: str = None, season: str = None,
                episode: str = None, tmdbid: int = None, dest: str = None):
        """
        据tmdbid、season、season_episode查询转移记录
        tmdbid + mtype 或 title + year 必输
        """
        # TMDBID + 类型
        if tmdbid and mtype:
            # 电视剧某季某集
            if season and episode:
                return db.query(TransferHistory).filter(TransferHistory.tmdbid == tmdbid,
                                                        TransferHistory.type == mtype,
                                                        TransferHistory.seasons == season,
                                                        TransferHistory.episodes == episode,
                                                        TransferHistory.dest == dest).all()
            # 电视剧某季
            elif season:
                return db.query(TransferHistory).filter(TransferHistory.tmdbid == tmdbid,
                                                        TransferHistory.type == mtype,
                                                        TransferHistory.seasons == season).all()
            else:
                if dest:
                    # 电影
                    return db.query(TransferHistory).filter(TransferHistory.tmdbid == tmdbid,
                                                            TransferHistory.type == mtype,
                                                            TransferHistory.dest == dest).all()
                else:
                    # 电视剧所有季集
                    return db.query(TransferHistory).filter(TransferHistory.tmdbid == tmdbid,
                                                            TransferHistory.type == mtype).all()
        # 标题 + 年份
        elif title and year:
            # 电视剧某季某集
            if season and episode:
                return db.query(TransferHistory).filter(TransferHistory.title == title,
                                                        TransferHistory.year == year,
                                                        TransferHistory.seasons == season,
                                                        TransferHistory.episodes == episode,
                                                        TransferHistory.dest == dest).all()
            # 电视剧某季
            elif season:
                return db.query(TransferHistory).filter(TransferHistory.title == title,
                                                        TransferHistory.year == year,
                                                        TransferHistory.seasons == season).all()
            else:
                if dest:
                    # 电影
                    return db.query(TransferHistory).filter(TransferHistory.title == title,
                                                            TransferHistory.year == year,
                                                            TransferHistory.dest == dest).all()
                else:
                    # 电视剧所有季集
                    return db.query(TransferHistory).filter(TransferHistory.title == title,
                                                            TransferHistory.year == year).all()
        return []

    @staticmethod
    def get_by_type_tmdbid(db: Session, mtype: str = None, tmdbid: int = None):
        """
        据tmdbid、type查询转移记录
        """
        return db.query(TransferHistory).filter(TransferHistory.tmdbid == tmdbid,
                                                TransferHistory.type == mtype).first()

    @staticmethod
    @db_persist
    def update_download_hash(db: Session, historyid: int = None, download_hash: str = None):
        db.query(TransferHistory).filter(TransferHistory.id == historyid).update(
            {
                "download_hash": download_hash
            }
        )
