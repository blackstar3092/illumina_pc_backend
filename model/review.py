# review.py
import logging
from sqlite3 import IntegrityError
from sqlalchemy import Text, JSON
from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User
from model.channel import Channel

class review(db.Model):
    """
    review Model
    
    The review class represents an individual contribution or discussion within a channel.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the review.
        _title (db.Column): A string representing the title of the review.
        _comment (db.Column): A string representing the comment of the review.
        _content (db.Column): A JSON blob representing the content of the review.
        _user_id (db.Column): An integer representing the user who created the review.
        _channel_id (db.Column): An integer representing the channel to which the review belongs.
    """
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _comment = db.Column(db.String(255), nullable=False)
    _content = db.Column(JSON, nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)

    def __init__(self, title, comment, user_id=None, channel_id=None, content={}, user_name=None, channel_name=None):
        """
        Constructor, 1st step in object creation.
        
        Args:
            title (str): The title of the review.
            comment (str): The comment of the review.
            user_id (int): The user who created the review.
            channel_id (int): The channel to which the review belongs.
            content (dict): The content of the review.
        """
        self._title = title
        self._comment = comment
        self._user_id = user_id
        self._channel_id = channel_id
        self._content = content

    def __repr__(self):
        """
        The __repr__ method is a special method used to represent the object in a string format.
        Called by the repr(review) built-in function, where review is an instance of the review class.
        
        Returns:
            str: A text representation of how to create the object.
        """
        return f"review(id={self.id}, title={self._title}, comment={self._comment}, content={self._content}, user_id={self._user_id}, channel_id={self._channel_id})"

    def create(self):
        """
        Creates a new review in the database.
        
        Returns:
            review: The created review object, or None on error.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not create review with title '{self._title}' due to {str(e)}.")
            return None
        return self
        
    def read(self):
        """
        The read method retrieves the object data from the object's attributes and returns it as a dictionary.
        
        Uses:
            The Channel.query and User.query methods to retrieve the channel and user objects.
        
        Returns:
            dict: A dictionary containing the review data, including user and channel names.
        """
        user = User.query.get(self._user_id)
        channel = Channel.query.get(self._channel_id)
        data = {
            "id": self.id,
            "title": self._title,
            "comment": self._comment,
            "content": self._content,
            "user_name": user.name if user else None,
            "channel_name": channel.name if channel else None
        }
        return data
    

    def update(self):
        """
        Updates the review object with new data.
        
        Args:
            inputs (dict): A dictionary containing the new data for the review.
        
        Returns:
            review: The updated review object, or None on error.
        """
        
        inputs = review.query.get(self.id)
        
        title = inputs._title
        content = inputs._content
        channel_id = inputs._channel_id
        user_name = User.query.get(inputs._user_id).name if inputs._user_id else None
        channel_name = Channel.query.get(inputs._channel_id).name if inputs._channel_id else None

        # If channel_name is provided, look up the corresponding channel_id
        if channel_name:
            channel = Channel.query.filter_by(_name=channel_name).first()
            if channel:
                channel_id = channel.id
                
        if user_name:
            user = User.query.filter_by(_name=user_name).first()
            if user:
                user_id = user.id
            else:
                return None

        # Update table with new data
        if title:
            self._title = title
        if content:
            self._content = content
        if channel_id:
            self._channel_id = channel_id
        if user_id:
            self._user_id = user_id

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not update review with title '{title}' due to missing channel_id.")
            return None
        return self
    
    def delete(self):
        """
        The delete method removes the object from the database and commits the transaction.
        
        Uses:
            The db ORM methods to delete and commit the transaction.
        
        Raises:
            Exception: An error occurred when deleting the object from the database.
        """    
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def restore(data):
        for review_data in data:
            _ = review_data.pop('id', None)  # Remove 'id' from review_data
            title = review_data.get("title", None)
            review = review.query.filter_by(_title=title).first()
            if review:
                review.update(review_data)
            else:
                review = review(**review_data)
                review.update(review_data)
                review.create()
        
def initreviews():
    """
    The initreviews function creates the review table and adds tester data to the table.
    
    Uses:
        The db ORM methods to create the table.
    
    Instantiates:
        review objects with tester data.
    
    Raises:
        IntegrityError: An error occurred when adding the tester data to the table.
    """        
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        reviews = [
            review(title='Added Group and Channel Select', comment='The Home Page has a Section, on this page we can select Group and Channel to allow blog filtering', content={'type': 'announcement'}, user_id=1, channel_id=1),
            review(title='JSON content saving through content"field in database', comment='You could add other dialogs to a review that would allow custom data or even storing reference to uploaded images.', content={'type': 'announcement'}, user_id=1, channel_id=1),
            review(title='Allows review by different Users', comment='Different users seeing content is a key concept in social media.', content={'type': 'announcement'}, user_id=2, channel_id=1),
        ]
        
        for review in reviews:
            try:
                review.create()
                print(f"Record created: {repr(review)}")
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {review._title}")