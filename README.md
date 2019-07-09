# Image Server

The image server project is designed to give the user a way to upload images to a remote server and have automatic cataloging and deduplication. The project has the backend user in mind along with a possible simple front end that can display images.


There are no actions assumed on each post and the subsequent actions aren't entirely thread safe - ie if two controllers call the `create-thumbnail` endpoint, then it is entirely possible that two thumbnails will be created. 

All of the multi-processing will take place server side while the client can just sit back and relax. 


## API Layout and Design
This API is a combination of REST like API calls and RPC oriented calls. 
Content can be uploaded and downloaded through Rest API calls while modifying actions will take place over RPC style calls. 

Example:
- Uploading an image `/upload/` - POST
- Get list of images needing thumbnails `/operations/thumbnails/missing` - GET
- Generating a job for thumbnails `/operations/thumbnails/generate` - POST

### Current API Design

```
/v1
    /upload
        / : POST (uploads image)
    /operations
        /thumbnails    : GET (gets list of thumbnails)
            /missing   : GET
            /generate  : POST
        /full-size     : GET (gets list of full-size images)
            /missing   : GET
            /generate  : POST
    /images            : GET - returns IDs of images matching search criteria
        /{id}
            /original  : GET, DELETE
            /full-size : GET, DELETE
            /thumbnail : GET, DELETE
            /metadata  : GET
        
```

### Database Design 
    
The current design is to include all of the entries in a single table. There is not a need at the moment to expand to multiple tables. Once de-duplication is added, there may be a more structured database schema. 

The current design is splitting the information between two tables. The first table contains the image metadata about the 


| id               | date_taken | date_added         | tags |
| :--------------: | :--------: | :----------------: | :--: |   
| UUID PRIMARY KEY | TIMESTAMP  | TIMESTAMP NOT NULL | JSON |


| id               | path          | format        | image_type    | date_uploaded      |
| :--------------: | :-----------: | :-----------: | :-----------: | :----------------: |
| UUID PRIMARY KEY | TEXT NOT NULL | TEXT NOT NULL | TEXT NOT NULL | TIMESTAMP NOT NULL |



### File Save path

The files are saved under a date partitioned naming structure based off of the date they were taken. If there is not a date taken, then it is defaulted to 2000/01/01. 
The leading folder is the type of image (full size, original, thumbnail etc) then the following directories are 

## Sample commands 
For upload a new image: 
```bash
curl -X POST http://localhost:5000/upload/ -F "file=@bb.jpg"
```
