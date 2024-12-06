-- Start Server : sudo mysqld_safe
-- Login to MariaDB Server : sudo mariadb
-- Use Database: use mysql
-- ALTER USER 'root'@'localhost' IDENTIFIED BY 'Root@123';
-- FLUSH PRIVILEGES;
-- Pre-requisite


CREATE SCHEMA GenesisCareer;
USE GenesisCareer;


-- Create OrganizationType table
CREATE TABLE OrganizationType (
    Id VARCHAR(50) PRIMARY KEY DEFAULT UUID() NOT NULL UNIQUE,
    Type VARCHAR(100) NOT NULL
); 

-- Insert data into OrganizationType table
INSERT INTO OrganizationType (Type) 
VALUES 
    ('College'), 
    ('School'), 
    ('MNC'), 
    ('IT'), 
    ('Finance'), 
    ('Healthcare'), 
    ('Retail'), 
    ('NGO'), 
    ('Government'), 
    ('Consulting');

-- Create Organization table
CREATE TABLE Organization (
    Id VARCHAR(50) PRIMARY KEY DEFAULT UUID() NOT NULL UNIQUE,
    Name VARCHAR(255) NOT NULL,
    WebsiteUrl VARCHAR(255),
    Location VARCHAR(255),
    OrganizationTypeId VARCHAR(50) NOT NULL, FOREIGN KEY (OrganizationTypeId) REFERENCES OrganizationType(Id)
);

-- Insert data into Organization table
INSERT INTO Organization (Name, OrganizationTypeId, WebsiteUrl, Location)
VALUES 
('TechCorp', (SELECT Id FROM OrganizationType WHERE Type = 'College'), 'https://www.techcorp.com', 'San Francisco, CA'),
('Helping Hands', (SELECT Id FROM OrganizationType WHERE Type = 'School'), 'https://www.helpinghands.org', 'New York, NY'),
('LearnAcademy', (SELECT Id FROM OrganizationType WHERE Type = 'MNC'), 'https://www.learnacademy.edu', 'Boston, MA'),
('City Council', (SELECT Id FROM OrganizationType WHERE Type = 'IT'), 'https://www.citycouncil.gov', 'Los Angeles, CA');



-- Create UserType table
CREATE TABLE UserType (
    Id VARCHAR(50) PRIMARY KEY DEFAULT UUID() NOT NULL UNIQUE,
    Type VARCHAR(50) NOT NULL UNIQUE -- Example: 'Admin', 'User', etc.
);

-- Insert data into UserType table
INSERT INTO UserType (Type) 
VALUES 
    ('Student'),
    ('Employer'),
    ('Employee'),
    ('Intern'),
    ('Fresher'),
    ('Experienced');

-- Create Users table
CREATE TABLE Users (
    Id VARCHAR(50) PRIMARY KEY DEFAULT UUID() NOT NULL UNIQUE,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Username VARCHAR(255) UNIQUE NOT NULL, 
    Password VARCHAR(100) NOT NULL, 
    Contact VARCHAR(15) UNIQUE NOT NULL,
    ProfilePic LONGBLOB NOT NULL,
    Resume LONGBLOB NOT NULL,
    Skills VARCHAR(50) NOT NULL,
    UserTypeId VARCHAR(50) NOT NULL, FOREIGN KEY (UserTypeId) REFERENCES UserType(Id),
    OrganizationId VARCHAR(50) NOT NULL, FOREIGN KEY (OrganizationId) REFERENCES ORGANIZATION(Id)
);


-- Create JobPosting table
CREATE TABLE JobPosting (
    Id VARCHAR(50) PRIMARY KEY DEFAULT UUID() NOT NULL UNIQUE,
    -- Username VARCHAR(255) NOT NULL,
    Created DATE DEFAULT CURRENT_DATE,
    LastDate DATE NOT NULL,
    UrlToApply VARCHAR(255) NOT NULL,
    Title VARCHAR(255) NOT NULL,
    WhoCanApply VARCHAR(100) NOT NULL,
    Description TEXT,
    RequiredSkillSet TEXT,
    UserId VARCHAR(50) NOT NULL, FOREIGN KEY (UserId) REFERENCES Users(Id)
);

SELECT * FROM JobPosting;

-- Create Applications table
CREATE TABLE Applications (
    Id VARCHAR(50) PRIMARY KEY DEFAULT UUID() NOT NULL UNIQUE,
    AppliedOn DATE DEFAULT CURRENT_DATE,
    JobId VARCHAR(50) NOT NULL, FOREIGN KEY (JobId) REFERENCES JobPosting(Id),
    UserId VARCHAR(50) NOT NULL UNIQUE, FOREIGN KEY (UserId) REFERENCES Users(Id),
    ProcessStep ENUM('Applied', 'Reviewed', 'Interview', 'Offered') NOT NULL
);

SELECT * 
FROM Users 
WHERE UserTypeId IN (SELECT Id FROM UserType WHERE Type != 'Employer');