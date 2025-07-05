import factory
from factory import Faker

from src.db.models.user import Organization, User

from .base import BaseFactory


class OrganizationFactory(BaseFactory):
    class Meta:
        model = Organization

    name = Faker("company")
    logo = Faker("image_url", width=200, height=200)
    address = Faker("address")
    phone_number = Faker("phone_number")


class UserFactory(BaseFactory):
    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword123")
    role = Faker("random_element", elements=["admin", "user", "manager", "viewer"])

    # Optional relationship - can be None or linked to an organization
    organization = factory.SubFactory(OrganizationFactory)
