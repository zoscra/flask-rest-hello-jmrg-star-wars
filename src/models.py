from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)

    favorite: Mapped["Favorite"] = relationship("Favorite", back_populates= "User")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
            "nickname": self.nickname
        }
class Planets(db.Model):
    __tablename__="planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    habitable: Mapped[str]= mapped_column(String(100), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            # do not serialize the password, its a security breach
            "name": self.name,
            "habitable": self.habitable
        }
    
class Characters(db.Model):
    __tablename__="characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    planeta_nacimieto: Mapped[int]= mapped_column(Integer, ForeignKey("planets.id"))

    Planets: Mapped["Planets"] = relationship("Planets")
    

    def serialize(self):
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            # do not serialize the password, its a security breach
            "name": self.name,
            "planeta_nacimieto": self.planeta_nacimieto
        }


class Favorite(db.Model):
    __tableName__="favorite"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id),nullable= False)
    planets_id: Mapped[int] = mapped_column(Integer, ForeignKey(Planets.id),nullable= True)
    characters_id: Mapped[int] = mapped_column(Integer, ForeignKey(Characters.id),nullable= True)

    characters: Mapped["Characters"] = relationship("Characters")
    planet: Mapped["Planets"] = relationship("Planets")
    user: Mapped["User"] = relationship("User", back_populates= "favorite")
