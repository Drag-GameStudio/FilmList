from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel


class BaseRepository:
    def __init__(self, session_factory, model):
        self.session_factory = session_factory
        self.model = model
        self.curr_session = None

    def get_session(self):
        if self.curr_session is None:
            self.curr_session = self.session_factory()
        
        return self.curr_session
    
    def read_by_options(self, schema: BaseModel, eager: bool = False) -> dict:
        session: Session = self.get_session()

        schema_dict = schema.model_dump()
        filled_schema_dict = [(key, schema_dict[key]) for key in schema_dict if schema_dict[key] is not None]
        
        query = session.query(self.model)
        for param in filled_schema_dict:
            query = query.filter(getattr(self.model, param[0]) == param[1])

        return {"all": query.all(), "query": query}
        
    def create(self, schema: BaseModel):
        session: Session = self.get_session()
        query = self.model(**schema.model_dump())
        try:
            session.add(query)
            session.commit()
            session.refresh(query)
        except Exception as e:
            session.rollback() 
            return False, None
        return True, query

    def read_by_id(self, schema: BaseModel, eager: bool = False) -> any:
        return self.read_by_options(schema, eager=eager).get("query").first()

    def update_element_by_id(self, schema_id: BaseModel, change_schema: BaseModel) -> any:
        curr_object = self.read_by_id(schema_id)
        if curr_object is None:
            return None
        
        schema_dict = change_schema.model_dump()
        filled_schema_dict = [(key, schema_dict[key]) for key in schema_dict if schema_dict[key] is not None]

        session: Session = self.get_session()
        session: Session
        for key in filled_schema_dict:
            setattr(curr_object, key, filled_schema_dict[key])
            session.commit()
            session.refresh()

        return curr_object
    
    def delete_object(self, schema: BaseModel):
        
        
        session: Session = self.get_session()
        curr_object = self.read_by_id(schema)
        if curr_object is None:
            return False

        session.delete(curr_object)
        session.commit()

        return True
    
    def __del__(self):
        if self.curr_session is not None:
            self.curr_session.close()

