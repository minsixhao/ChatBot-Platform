from datetime import datetime

@router.post("/bots/", response_model=Bot)
def create_bot(bot: BotCreate, db: Session = Depends(get_db)):
    db_bot = crud.create_bot(db, bot)
    if db_bot.created_at is None:
        db_bot.created_at = datetime.utcnow()
    if db_bot.updated_at is None:
        db_bot.updated_at = datetime.utcnow()
    return db_bot