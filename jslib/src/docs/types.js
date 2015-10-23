/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * A string containing a reference to an object.
 *
 * The object reference identifies a specific data object within a KBase workspace.
 * Note that the object reference is only valid within a specific workspace runtime,
 * such as Dev, CI, Staging, or Production.
 *
 * The KBase object reference can take two forms:
 * workspace/id/version
 * workspace/id
 *
 * The canonical refeference format is the first, in that it maps to a specific
 * object and version. The second form does not identify an actual object, but
 * rather is a shorthand to the "most recent" version of an object; that is, the
 * object with the given id with the greatest version. The object may be
 * inspected through the data api to determine the specific version.
 *
 * @typedef {String} ObjectReference
 */
