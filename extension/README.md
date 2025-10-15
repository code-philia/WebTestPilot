This is a VSCode Extension for managing NL-based (Natural Language) GUI Test cases

It will have an interface similar to Postman.

User can manage:
- Folders
- Nested folders
- Test cases (in the form of .json files)

Sample testcase format:
```json
{
  "name": "32::Credit Mark Sent",
  "url": "http://localhost:8082/",
  "actions": [
    {
      "action": "Click \"More Actions\" dropdown button",
      "expectedResult": "Actions menu opens"
    },
    {
      "action": "Click \"Mark Sent\" option",
      "expectedResult": "The status of credit is updated to Sent"
    },
    {
      "action": "Verify credit status changes to \"Sent\"",
      "expectedResult": "Credit status indicator shows \"\"Sent\"\""
    }
  ]
}
```

Storage mechanism: All data is stored in the current workspace's .webtestpilot folder, and then all files and folders will mirror the structure and data inside .webtestpilot folder.

Input mechanism:
- 1 test case has the following metadata: Name, URL.
- Then user needs to specify `actions`: which is a list of "action" and "expectedResult". As shown in the sample. This part should have easy mechanism for user to edit, delete, add new steps.

Test case run mechanism:
- Detailed process: TBD, will be filled later.
- User interface: it will load up a Webview that will connect to a playwright browser session and show it live to visualize it.
- User can run indivisual test cases or run a folder of test cases.


USER FLOW 1:
Some sample user flow:
- User create test cases, folders consisting of test cases.
- User can run the test case or the folder of test cases.
- The system then reports back the status of test cases, pass/fail, ...

USER FLOW 2:
Sample of AI-powered (requirements processing) user flow:
- TBD
