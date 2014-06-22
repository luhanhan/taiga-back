# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014 Anler Hernández <hello@anler.me>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

from django.core.urlresolvers import reverse

from .. import factories as f


pytestmark = pytest.mark.django_db

@pytest.fixture
def searches_initial_data():
    m = type("InitialData", (object,), {})()

    m.project1 = f.ProjectFactory.create()
    m.project2 = f.ProjectFactory.create()

    m.member1 = f.MembershipFactory.create(project=m.project1)
    m.member2 = f.MembershipFactory.create(project=m.project1)

    m.us1 = f.UserStoryFactory.create(project=m.project1)
    m.us2 = f.UserStoryFactory.create(project=m.project1, description="Back to the future")
    m.us3 = f.UserStoryFactory.create(project=m.project2)

    m.tsk1 = f.TaskFactory.create(project=m.project2)
    m.tsk2 = f.TaskFactory.create(project=m.project1)
    m.tsk3 = f.TaskFactory.create(project=m.project1, subject="Back to the future")

    m.iss1 = f.IssueFactory.create(project=m.project1, subject="Backend and Frontend")
    m.iss2 = f.IssueFactory.create(project=m.project2)
    m.iss3 = f.IssueFactory.create(project=m.project1)

    m.wiki1  = f.WikiPageFactory.create(project=m.project1)
    m.wiki2  = f.WikiPageFactory.create(project=m.project1, content="Frontend, future")
    m.wiki3  = f.WikiPageFactory.create(project=m.project2)

    return m


def test_search_all_objects_in_my_project(client, searches_initial_data):
    data = searches_initial_data

    client.login(data.member1.user)

    response = client.get(reverse("search-list"), {"project": data.project1.id})
    assert response.status_code == 200
    assert response.data["count"] == 8
    assert len(response.data["userstories"]) == 2
    assert len(response.data["tasks"]) == 2
    assert len(response.data["issues"]) == 2
    assert len(response.data["wikipages"]) == 2


def test_search_all_objects_in_project_is_not_mine(client, searches_initial_data):
    data = searches_initial_data

    client.login(data.member1.user)

    response = client.get(reverse("search-list"), {"project": data.project2.id})
    assert response.status_code == 403


def test_search_text_query_in_my_project(client, searches_initial_data):
    data = searches_initial_data

    client.login(data.member1.user)

    response = client.get(reverse("search-list"), {"project": data.project1.id, "text": "future"})
    assert response.status_code == 200
    assert response.data["count"] == 3
    assert len(response.data["userstories"]) == 1
    assert len(response.data["tasks"]) == 1
    assert len(response.data["issues"]) == 0
    assert len(response.data["wikipages"]) == 1

    response = client.get(reverse("search-list"), {"project": data.project1.id, "text": "back"})
    assert response.status_code == 200
    assert response.data["count"] == 2
    assert len(response.data["userstories"]) == 1
    assert len(response.data["tasks"]) == 1
    assert len(response.data["issues"]) == 0
    assert len(response.data["wikipages"]) == 0
