from datetime import datetime

def create_bot(db: Session, bot: BotCreate) -> Bot:
    db_bot = BotDB(**bot.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return Bot.from_orm(db_bot)