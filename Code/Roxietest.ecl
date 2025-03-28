IMPORT $, STD, code.File_AllData;

// Roxie Search Query
EXPORT FindMissingKid(STRING25 in_city = '', STRING2 in_state = '', STRING18 in_first = '', STRING24 in_last = '', UNSIGNED4 in_dateMissing = 0) := FUNCTION

    Filtered := File_AllData.mc_byStateDS(
        (in_city = '' OR MissingCity = in_city) AND
        (in_state = '' OR MissingState = in_state) AND
        (in_first = '' OR FirstName = in_first) AND
        (in_last = '' OR LastName = in_last) AND
        (in_dateMissing = 0 OR DateMissing = in_dateMissing)
    );

    RETURN OUTPUT(Filtered, NAMED('MissingKidResults'));

END;
