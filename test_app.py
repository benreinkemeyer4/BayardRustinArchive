
import unittest
import urllib.parse
from database.query_db import query_db
from database.insert_db import insert_db
from database.query_singleitem_db import query_singleitem_db
from database.approve_sub import approve_sub
from database.unapprove_sub import unapprove_sub
from database.delete_db import delete_db
from database.edit_db import edit_db
from datetime import date
from database.query_admin import query_admin


# parse youtube url and return unique key
def video_id(value):
    query = urllib.parse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self._link1 = "http://youtu.be/SA2iWivDJiE"
        self._link2 = "http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu"
        self._link3 = "http://www.youtube.com/embed/SA2iWivDJiE"
        self._link4 = "http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US"



        self._submission =  {
                "submitter-name": "Test",
                "date_taken": date.today(),
                "submitter-email": "Test",
                "submitter-pronouns": "Test",
                "tags": "Test",
                "title": "Test",
                "description": "Test",
                "media_url": "https://www.youtube.com/embed/rD-ItELhG88",
                "media_type": "Video"
            }
        self._media_id = "24"


class VideoIDTestCase1(AppTestCase):
    def runTest(self):
        id = video_id(self._link1)
        expected = "SA2iWivDJiE"
        self.assertEqual(id, expected, "Incorrect id 1")
class VideoIDTestCase2(AppTestCase):
    def runTest(self):
        id = video_id(self._link2)
        expected = "_oPAwA_Udwc"
        self.assertEqual(id, expected, "Incorrect id 2")
class VideoIDTestCase3(AppTestCase):
    def runTest(self):
        id = video_id(self._link3)
        expected = "SA2iWivDJiE"
        self.assertEqual(id, expected, "Incorrect id 3")
class VideoIDTestCase4(AppTestCase):
    def runTest(self):
        id = video_id(self._link4)
        expected = "SA2iWivDJiE"
        self.assertEqual(id, expected, "Incorrect id 4")



class InsertEditDeleteDBTestCase(AppTestCase):
    def runTest(self):
        result = insert_db(self._submission)

        media_id = None
        if not result["error"]:
            media_id = result["res"]

        expected = False
        self.assertEqual(result["error"], expected, "Incorrect insert")

        if media_id:

            submission = {
                 "submitter-name": "Test",
                "date_taken": date.today(),
                "submitter-email": "Test",
                "submitter-pronouns": "Test",
                "tags": "Test",
                "title": "Test",
                "description": "Test",
                "mediaid": media_id
            }

            result = edit_db(submission)
            expected = True

            self.assertEqual(result, expected, "Incorrect edit")


            result = delete_db(media_id)
            expected = True

            self.assertEqual(result, expected, "Incorrect delete")


class QueryDBTestCase(AppTestCase):
    def runTest(self):
        result = query_db()
        expected = False
        self.assertEqual(result["error"], expected, "Incorrect query")

class QuerySingleItemDBTestCase(AppTestCase):
    def runTest(self):
        result =  query_singleitem_db(self._media_id)
        expected = False
        self.assertEqual(result["error"], expected, "Incorrect query single item")
class QueryAdminDBTestCase(AppTestCase):
    def runTest(self):
        result =  query_admin()
        expected = False
        self.assertEqual(result["error"], expected, "Incorrect query admin")

class UnapproveApproveDBTestCase(AppTestCase):
    def runTest(self):
        res = unapprove_sub(self._media_id)
        expected = True
        self.assertEqual(res, expected, "Incorrect unapproval")

        res = approve_sub(self._media_id)
        expected = True
        self.assertEqual(res, expected, "Incorrect approval")



if __name__ == "__main__":
    unittest.main()
