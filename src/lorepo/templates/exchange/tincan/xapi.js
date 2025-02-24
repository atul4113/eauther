/*!
    Copyright 2015 Learnetic SA

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/
/**
 * Provides the xAPI convenience class for initialization and usage of tincan js. It helps to prepare and send
 * xAPI statements that conform to the SCORM Experience API profile
 * https://github.com/adlnet/xAPI-SCORM-Profile/blob/master/xapi-scorm-profile.md
 *
 * @module xAPI
 */
(function (window) {

    var statementCfg = {doStamp: true};


    function generateAttemptIRI(xapi) {
        var attemptTAG = TinCan.Utils.getUUID();
        return xapi.courseIRI.toString()+"/"+xapi.lessonIRI.toString()+"?attemptId="+attemptTAG
    }


    function getAttemptObject(xapi) {
        var activity = {
                id: xapi.attemptIRI,
                definition: {
                    name: {
                        "en-US": "Attempt for " + xapi.lessonTitle
                    },
                    "description": {
                        "en-US": "Activity representing an attempt for " + xapi.lessonTitle
                    },
                    "type": "http://adlnet.gov/expapi/activities/attempt"
                }
            };
        return activity;
    }


    function getCourseObject(xapi) {
        var activity = {
                "id": xapi.courseIRI
        };
        if(xapi.courserTitle || xapi.courseDescription){
            activity.definition = {
                name: {
                    "en-US": xapi.courserTitle
                },
                description: {
                    "en-US": xapi.courseDescription
                },
                type: "http://adlnet.gov/expapi/activities/course"
            }
        }

        return activity;
    }

    function getContext(xapi){
        var context = {
                "contextActivities": {
                    "grouping": [
                                    getAttemptObject(xapi),
                                    getCourseObject(xapi)
                                ],
                    "category": [
                                   {
                                      "id": "http://adlnet.gov/xapi/profile/scorm"
                                   }
                                ]
                }
        };
        return context;
    }

    function getEndStatement(xapi, verb, score){
        var tincanScore = new TinCan.Score(score);
        var statement = xapi.tincan.prepareStatement({
            "verb": verb,
            "context": getContext(xapi),
            "result": {
                score: tincanScore,
                duration: score.duration.toString()
            }
        }, statementCfg);
        return statement;
    }

    function updateAttemptsArray(xapi){
        var state = null;
        try {
            var state = xapi.tincan.getState("http://adlnet.gov/xapi/profile/scorm/activity-state");
        }catch(err) {}

        var contents = {};
        if (state && state.state) {
            contents = state.state.contents;
        }
        if (typeof contents.attempts === "undefined"){
            contents = {attempts: [xapi.attemptIRI]};
        }else {
            //make sure the new attemptIRI is unique
            while(contents.attempts.indexOf(xapi.attemptIRI) != -1){
                xapi.attemptIRI = generateAttemptIRI(xapi);
            }
            contents.attempts.push(xapi.attemptIRI);
        }

        xapi.tincan.setState(
            "http://adlnet.gov/xapi/profile/scorm/activity-state",
            contents,
            {contentType:"application/json"}
        );
    }

    function validateConfig(cfg){
        var obligatory = [  "endpoint", "actor", "lessonIRI", "courseIRI", "lessonTitle", "entry"];

        if(!cfg){
            throw "Configuration is empty"
        }
        for (var i = 0; i < obligatory.length; i++ ){
            if(!cfg[obligatory[i]]){
                throw "No " + obligatory[i] + " provided."
            }
        }
        if(cfg.entry == "resume" && !(cfg.attemptIRI)){
            throw "Entry is 'resume' but no attemptIRI found";
        }
    }

     /**
      * xAPI convenience class for initialization and usage of tincan js. It helps to prepare and send
      * xAPI statements that conform to the SCORM Experience API profile.
      * (https://github.com/adlnet/xAPI-SCORM-Profile/blob/master/xapi-scorm-profile.md)
      * Constructor Initializes xAPI SCORM Profile implementation.
      * This implementation depends on the availability of TinCanJS library
      * (https://github.com/RusticiSoftware/TinCanJS) and has been tested with TinCanJS build 0.33.0.
      * @class xAPI
      * @constructor xAPI
      * @param {Object} cfg Configuration
      * @param {String} [cfg.attemptIRI] Needs to be provided if this is a resume attempt action.
      * @param {String} cfg.courserIRI Uniquely identifies the course.
      * @param {String} [cfg.courserTitle] Recommended if not provided in params.
      * @param {String} [cfg.courseDescription] Recommended if not provided in params.
      * @param {String} cfg.endpoint LRS endpoint URL
      * @param {String} [cfg.auth] Authorization token for the LRS, will be passed in the "Authorization" header.
      * @param {String} [cfg.username] If no auth token is provided username and password will be user in basic auth.
      * @param {String} [cfg.password] If no auth token is provided username and password will be user in basic auth.
      * @param {String} cfg.lessonIRI Uniquely identifies this lesson in the scope of the course.
      * @param {String} cfg.lessonTitle
      * @param {String} cfg.lessonDescription
      * @param {String} cfg.entry "ab-initio" or "resume"
      * @param {Object} cfg.actor Identifies the user that attempts this lesson within the scope of the LMS.
      *     @param {Object} cfg.actor.account Recommended if not provided in params.
      *         @param {String} cfg.actor.account.homePage User origin, usually location of the LMS.
      *         @param {String} cfg.actor.account.name User identifier.
    */
    function xAPI(cfg) {
        validateConfig(cfg);

        var tincanCfg = {
            recordStores: [
                           {
                               "endpoint": cfg.endpoint,
                               "allowFail": false
                           }
                           ],
            actor: cfg.actor,
            activity: {
                "id" : cfg.courseIRI+ "/" + cfg.lessonIRI,
                "definition" :{
                    "name":{
                        "en-US":cfg.lessonTitle
                     },
                     "description":{
                         "en-US":cfg.lessonDescription
                      },
                     "type": "http://adlnet.gov/expapi/activities/lesson"
                }
            }
        };
        if(cfg.auth){
            tincanCfg.recordStores[0].auth = cfg.auth;
        }else if(cfg.username && cfg.password){
            tincanCfg.recordStores[0].username = cfg.username;
            tincanCfg.recordStores[0].password = cfg.password;
        }
        try {
            this.tincan = new TinCan(tincanCfg);
        }catch (err){
            throw "TinCanJS is  misconfigured or not available."
        }

        this.attemptIRI = cfg.attemptIRI;
        this.lessonIRI = cfg.lessonIRI;
        this.lessonTitle = cfg.lessonTitle;
        this.lessonDescription = cfg.lessonDescription;
        this.courseIRI = cfg.courseIRI;
        this.courseTitle = cfg.courseTitle;
        this.courseDescription = cfg.courseDescription;
    }


    /**
     * see http://stackoverflow.com/a/2880929
     * @method getParams
     */
    function getParams(){
         var match,
            pl     = /\+/g,  // Regex for replacing addition symbol with a space
            search = /([^&=]+)=?([^&]*)/g,
            decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
            query  = window.location.search.substring(1);

        params = {};
        while (match = search.exec(query))
           params[decode(match[1])] = decode(match[2]);

        return params;
    }

    /**
     * Composes cfg object trying to take values from GET params, using defaults if provided,
     * for most values. Others such as lesson description should not be passed through GET params, due to it's length.
     * @method configFromParams
     * @param {Object} [cfg] Default configuration
     *      @param {String} [cfg.attemptIRI] Needs to be provided if this is a resume attempt action.
     *      @param {String} [cfg.courserIRI] Obligatory if not provided in params.
     *      @param {String} [cfg.courserTitle] Recommended if not provided in params.
     *      @param {String} [cfg.courseDescription] Recommended if not provided in params.
     *      @param {String} [cfg.endpoint] LRS endpoint URL
     *      @param {String} [cfg.auth] Authorization token for the LRS, will be passed in the "Authorization" header.
     *      @param {String} [cfg.lessonIRI] Obligatory if not provided in the params.
     *      @param {String} cfg.lessonTitle
     *      @param {String} cfg.lessonDescription Recommended if not provided in params.
     *      @param {String} [cfg.entry] "ab-initio" or "resume"
     *      @param {Object} [cfg.actor] Obligatory if not provided in params.
     *          @param {Object} cfg.actor.account Recommended if not provided in params.
     *              @param {String} cfg.actor.account.homePage User origin, usually location of the LMS.
     *              @param {String} cfg.actor.account.name User identifier.
     * @return {Object} Config object with parameters fetched form the GET params.
        */
    xAPI.configFromParams = function(cfg){
        var params = getParams();
        cfg.attemptIRI = params.attemptIRI || cfg.attemptIRI;
        cfg.entry = params.entry || cfg.entry;
        cfg.courseIRI  = params.courseIRI || cfg.courseIRI;
        cfg.courseTitle = params.courseTitle || cfg.courseTitle;
        cfg.courseDescription = params.courseDescription || cfg.courseDescription;
        cfg.endpoint = params.endpoint || cfg.endpoint;
        cfg.auth = params.auth || cfg.auth;
        cfg.lessonIRI = params.lessonIRI || cfg.lessonIRI;
        cfg.lessonDescription = params.lessonDescription || cfg.lessonDescription;
        cfg.username = params.username || cfg.username;
        cfg.password = params.password || cfg.password;
        var actor = params.actor;
        if (actor){
            cfg.actor = JSON.parse(actor);
        }
        return cfg;
    }


    /**
     * Initializes an attempt. If no attemptIRI is provided one will be randomly generated. Sends an "initialize"
     * statement using Statement API and updates attempt IRI table in the LRS using State API.
     * @method initializeAttempt
     */
    xAPI.prototype.initializeAttempt = function(){
        this.attemptIRI = generateAttemptIRI(this);
        updateAttemptsArray(this);
        //create statement
        var statement = this.tincan.prepareStatement({
            "verb":{
                  "id":"http://adlnet.gov/expapi/verbs/initialized",
                  "display":{
                     "en-US":"initialized"
                  }
               },
            "context": getContext(this)
        }, statementCfg);
        this.tincan.sendStatement(statement);
    }

    /**
     * Sends current lesson's attempt state for storage in the LRS using State API. Current attemptIRI that identifies
     * this attempt is provided in cfg during initialization or randomly generated.
     * @method saveAttemptState
     * @param state
     *  @param state.location Integer value defining last visited lesson page number.
     *  @param state.state_string Base64 encoded state string from icPlayer.
     */
    xAPI.prototype.saveAttemptState = function(state){
        var attemptIRI = this.attemptIRI;
        var cfg = {
            contentType: "application/json",
            activity: getAttemptObject(this)
        };
        this.tincan.setState("http://adlnet.gov/xapi/profile/scorm/attempt-state", state, cfg);
    }


    /**
     * Fetch state of the current attempt. Either synchronously or asynchronousy - by providing a callback. Uses State
     * API.
     * @method getAttemptState
     * @param {Object} cfg Configuration
     * @param {Function} [cfg.callback] Provide a callback function for asynchronous usage.
     */
    xAPI.prototype.getAttemptState = function(cfg){

        var attemptIRI = this.attemptIRI;

        cfg = cfg || {};

        //change the activity to "attempt"
        var queryCfg = {
            activity:  {
                id: attemptIRI,
                name: {
                    "en-US": "Attempt for "+this.lessonTitle
                },
                "description":{
                    "en-US":"Activity represetin an attempt for " + this.lessonTitle
                },
                "type": "http://adlnet.gov/expapi/activities/attempt"
            }
        };
        if (typeof cfg.callback !== "undefined") {
            queryCfg.callback = cfg.callback;
        }

        return this.tincan.getState("http://adlnet.gov/xapi/profile/scorm/attempt-state",queryCfg);
    }


    /**
     * Sends an "resume" statement, attemptIRI has to be provided during initialization.
     * @method resumeAttempt
     */
    xAPI.prototype.resumeAttempt = function(){
        //send resume attempt statement
        var statement = this.tincan.prepareStatement({
            "verb":{
                  "id":"http://adlnet.gov/expapi/verbs/resumed",
                  "display":{
                     "en-US":"resumed"
                  }
               },
            "context": getContext(this)
        }, statementCfg);
        this.tincan.sendStatement(statement);
    }

    /**
     * @method suspendAttempt
     *  @param {Object} score Score object for this attempt. Sent with Statement API.
     *      @param {Number} score.max_score
     *      @param {Number} score.min_score
     *      @param {Number} score.raw_score
     *      @param {Number} score.scaled_score
     *      @param {String} [score.session_time]
     *  @param {Object} [state] Last page index and state string. Sent with State API.
     *      @param {String} state.state_string State string as returned by the icPlayer.
     *      @param {Number} [state.location] Last page index
        */
    xAPI.prototype.suspendAttempt = function(score, state){
        //send suspend attempt statement
        var verb = {
                  "id":"http://adlnet.gov/expapi/verbs/suspended",
                  "display":{
                     "en-US":"suspended"
                  }
               };
        var statement = getEndStatement(this, verb, score);
        this.tincan.sendStatement(statement);
        //send state to state API
        if (typeof state !== "undefined" && state !== null && typeof state.state_string !== "undefined") {
            this.saveAttemptState(state);
        }
    }

    /**
     *  @method completeAttempt
     *  @param {Object} score Score object for this attempt. Sent with Statement API.
     *      @param {Number} score.max_score
     *      @param {Number} score.min_score
     *      @param {Number} score.raw_score
     *      @param {Number} score.scaled_score
     *      @param {String} [score.session_time]
     *  @param {Object} [state] Last page index and state string. Sent with State API.
     *      @param {String} state.state_string State string as returned by the icPlayer.
     *      @param {Number} [state.location] Last page index
        */
    xAPI.prototype.completeAttempt = function(score, state) {
        //send complete attempt statement with scoring
        var verb = {
                  "id":"http://adlnet.gov/expapi/verbs/completed",
                  "display":{
                     "en-US":"completed"
                  }
               };
        var statement = getEndStatement(this, verb, score);
        this.tincan.sendStatement(statement);
        //send state to state API
        if (typeof state !== "undefined" && state !== null && typeof state.state_string !== "undefined") {
            this.saveAttemptState(state);
        }
    }

    /**
     *  @method terminateAttempt
     *  @param {Object} score Score object for this attempt. Sent with Statement API.
     *      @param {Number} score.max_score
     *      @param {Number} score.min_score
     *      @param {Number} score.raw_score
     *      @param {Number} score.scaled_score
     *      @param {String} [score.session_time]
     *  @param {Object} [state] Last page index and state string. Sent with State API.
     *      @param {String} state.state_string State string as returned by the icPlayer.
     *      @param {Number} [state.location] Last page index
        */
    xAPI.prototype.terminateAttempt = function(score, state) {
        var verb = {
                  "id":"http://adlnet.gov/expapi/verbs/terminated",
                  "display":{
                     "en-US":"terminated"
                  }
               };
        var statement = getEndStatement(this, verb, score);
        this.tincan.sendStatement(statement);
        //send state to state API
        if (state && state.state_string) {
            this.saveAttemptState(state);
        }
    }


    window.xAPI = window.xAPI || xAPI;
})(window);
