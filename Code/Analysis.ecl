IMPORT $, STD;
IMPORT File_AllData;


KidsDS := $.File_AllData.mc_byStateDS;

KidsRec := RECORD
    UNSIGNED3 RecID;
    STRING11  DatePosted;
    STRING18 FirstName;
    STRING24 LastName;
    UNSIGNED1 CurrentAge;
    UNSIGNED4 DateMissing;
    STRING25 MissingCity;
    STRING2  MissingState;
    STRING150 Contact;
    STRING100 PhotoLink;
    STRING10 AgeGroup;
END;

CleanKids := PROJECT(KidsDS, TRANSFORM(KidsRec,
    SELF.MissingCity := STD.STR.ToUpperCase(LEFT.MissingCity),
    SELF.MissingState := STD.STR.ToUpperCase(LEFT.MissingState),
    SELF.AgeGroup := MAP(
        LEFT.CurrentAge < 10 => 'Under10',
        LEFT.CurrentAge <= 17 => '10-17',
        '18+'
    ),
    SELF := LEFT
));



AgeGroups := TABLE(CleanKids,
    { 
        AgeGroup;
        UNSIGNED totalCases := COUNT(GROUP)
    },
    AgeGroup
);
OUTPUT(AgeGroups, NAMED('Age_Distribution'));

CityCounts := TABLE(CleanKids,
    { 
        MissingCity;
        MissingState;
        UNSIGNED totalCases := COUNT(GROUP)
    },
    MissingCity, MissingState
);
OUTPUT(CityCounts, NAMED('Cases_By_City'));



ExportForML := PROJECT(CleanKids, TRANSFORM({
        STRING25 city;
        STRING2 state;
        UNSIGNED1 age;
        UNSIGNED4 dateMissing
    },
    SELF.city := LEFT.MissingCity,
    SELF.state := LEFT.MissingState,
    SELF.age := LEFT.CurrentAge,
    SELF.dateMissing := LEFT.DateMissing
));

OUTPUT(ExportForML,,'~output::kids_features',CSV(SEPARATOR(','), TERMINATOR('\n')));
