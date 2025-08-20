import factory
from factory import Faker

from src.db.models.user import Organization, OrganizationMember, User, UserRole
from tests.factories.base import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    password = "fake_password_hash"  # Fast fake password for tests
    password_must_change = False


class OrganizationFactory(BaseFactory):
    class Meta:
        model = Organization

    name = Faker("company")
    logo = Faker("image_url", width=200, height=200)
    address = Faker("address")
    phone_number = Faker("phone_number")
    created_by = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def created_by_user_id(self):
        return self.created_by.id


class OrganizationMemberFactory(BaseFactory):
    class Meta:
        model = OrganizationMember

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)
    role = UserRole.RADIOLOGIST.value

    @factory.lazy_attribute
    def user_id(self):
        return self.user.id

    @factory.lazy_attribute
    def organization_id(self):
        return self.organization.id
