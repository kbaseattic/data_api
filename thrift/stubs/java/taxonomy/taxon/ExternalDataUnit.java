/**
 * Autogenerated by Thrift Compiler (0.9.2)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
package taxon;

import org.apache.thrift.scheme.IScheme;
import org.apache.thrift.scheme.SchemeFactory;
import org.apache.thrift.scheme.StandardScheme;

import org.apache.thrift.scheme.TupleScheme;
import org.apache.thrift.protocol.TTupleProtocol;
import org.apache.thrift.protocol.TProtocolException;
import org.apache.thrift.EncodingUtils;
import org.apache.thrift.TException;
import org.apache.thrift.async.AsyncMethodCallback;
import org.apache.thrift.server.AbstractNonblockingServer.*;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.EnumMap;
import java.util.Set;
import java.util.HashSet;
import java.util.EnumSet;
import java.util.TreeSet;
import java.util.TreeMap;
import java.util.Collections;
import java.util.BitSet;
import java.nio.ByteBuffer;
import java.util.Arrays;
import javax.annotation.Generated;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings({"cast", "rawtypes", "serial", "unchecked"})
@Generated(value = "Autogenerated by Thrift Compiler (0.9.2)", date = "2015-11-12")
public class ExternalDataUnit implements org.apache.thrift.TBase<ExternalDataUnit, ExternalDataUnit._Fields>, java.io.Serializable, Cloneable, Comparable<ExternalDataUnit> {
  private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("ExternalDataUnit");

  private static final org.apache.thrift.protocol.TField RESOURCE_NAME_FIELD_DESC = new org.apache.thrift.protocol.TField("resource_name", org.apache.thrift.protocol.TType.STRING, (short)1);
  private static final org.apache.thrift.protocol.TField RESOURCE_URL_FIELD_DESC = new org.apache.thrift.protocol.TField("resource_url", org.apache.thrift.protocol.TType.STRING, (short)2);
  private static final org.apache.thrift.protocol.TField RESOURCE_VERSION_FIELD_DESC = new org.apache.thrift.protocol.TField("resource_version", org.apache.thrift.protocol.TType.STRING, (short)3);
  private static final org.apache.thrift.protocol.TField RESOURCE_RELEASE_DATE_FIELD_DESC = new org.apache.thrift.protocol.TField("resource_release_date", org.apache.thrift.protocol.TType.STRING, (short)4);
  private static final org.apache.thrift.protocol.TField DATA_URL_FIELD_DESC = new org.apache.thrift.protocol.TField("data_url", org.apache.thrift.protocol.TType.STRING, (short)5);
  private static final org.apache.thrift.protocol.TField DATA_ID_FIELD_DESC = new org.apache.thrift.protocol.TField("data_id", org.apache.thrift.protocol.TType.STRING, (short)6);
  private static final org.apache.thrift.protocol.TField DESCRIPTION_FIELD_DESC = new org.apache.thrift.protocol.TField("description", org.apache.thrift.protocol.TType.STRING, (short)7);

  private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
  static {
    schemes.put(StandardScheme.class, new ExternalDataUnitStandardSchemeFactory());
    schemes.put(TupleScheme.class, new ExternalDataUnitTupleSchemeFactory());
  }

  public String resource_name; // required
  public String resource_url; // required
  public String resource_version; // required
  public String resource_release_date; // required
  public String data_url; // required
  public String data_id; // required
  public String description; // required

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements org.apache.thrift.TFieldIdEnum {
    RESOURCE_NAME((short)1, "resource_name"),
    RESOURCE_URL((short)2, "resource_url"),
    RESOURCE_VERSION((short)3, "resource_version"),
    RESOURCE_RELEASE_DATE((short)4, "resource_release_date"),
    DATA_URL((short)5, "data_url"),
    DATA_ID((short)6, "data_id"),
    DESCRIPTION((short)7, "description");

    private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

    static {
      for (_Fields field : EnumSet.allOf(_Fields.class)) {
        byName.put(field.getFieldName(), field);
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, or null if its not found.
     */
    public static _Fields findByThriftId(int fieldId) {
      switch(fieldId) {
        case 1: // RESOURCE_NAME
          return RESOURCE_NAME;
        case 2: // RESOURCE_URL
          return RESOURCE_URL;
        case 3: // RESOURCE_VERSION
          return RESOURCE_VERSION;
        case 4: // RESOURCE_RELEASE_DATE
          return RESOURCE_RELEASE_DATE;
        case 5: // DATA_URL
          return DATA_URL;
        case 6: // DATA_ID
          return DATA_ID;
        case 7: // DESCRIPTION
          return DESCRIPTION;
        default:
          return null;
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, throwing an exception
     * if it is not found.
     */
    public static _Fields findByThriftIdOrThrow(int fieldId) {
      _Fields fields = findByThriftId(fieldId);
      if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
      return fields;
    }

    /**
     * Find the _Fields constant that matches name, or null if its not found.
     */
    public static _Fields findByName(String name) {
      return byName.get(name);
    }

    private final short _thriftId;
    private final String _fieldName;

    _Fields(short thriftId, String fieldName) {
      _thriftId = thriftId;
      _fieldName = fieldName;
    }

    public short getThriftFieldId() {
      return _thriftId;
    }

    public String getFieldName() {
      return _fieldName;
    }
  }

  // isset id assignments
  public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
  static {
    Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.RESOURCE_NAME, new org.apache.thrift.meta_data.FieldMetaData("resource_name", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.RESOURCE_URL, new org.apache.thrift.meta_data.FieldMetaData("resource_url", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.RESOURCE_VERSION, new org.apache.thrift.meta_data.FieldMetaData("resource_version", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.RESOURCE_RELEASE_DATE, new org.apache.thrift.meta_data.FieldMetaData("resource_release_date", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.DATA_URL, new org.apache.thrift.meta_data.FieldMetaData("data_url", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.DATA_ID, new org.apache.thrift.meta_data.FieldMetaData("data_id", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.DESCRIPTION, new org.apache.thrift.meta_data.FieldMetaData("description", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(ExternalDataUnit.class, metaDataMap);
  }

  public ExternalDataUnit() {
  }

  public ExternalDataUnit(
    String resource_name,
    String resource_url,
    String resource_version,
    String resource_release_date,
    String data_url,
    String data_id,
    String description)
  {
    this();
    this.resource_name = resource_name;
    this.resource_url = resource_url;
    this.resource_version = resource_version;
    this.resource_release_date = resource_release_date;
    this.data_url = data_url;
    this.data_id = data_id;
    this.description = description;
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public ExternalDataUnit(ExternalDataUnit other) {
    if (other.isSetResource_name()) {
      this.resource_name = other.resource_name;
    }
    if (other.isSetResource_url()) {
      this.resource_url = other.resource_url;
    }
    if (other.isSetResource_version()) {
      this.resource_version = other.resource_version;
    }
    if (other.isSetResource_release_date()) {
      this.resource_release_date = other.resource_release_date;
    }
    if (other.isSetData_url()) {
      this.data_url = other.data_url;
    }
    if (other.isSetData_id()) {
      this.data_id = other.data_id;
    }
    if (other.isSetDescription()) {
      this.description = other.description;
    }
  }

  public ExternalDataUnit deepCopy() {
    return new ExternalDataUnit(this);
  }

  @Override
  public void clear() {
    this.resource_name = null;
    this.resource_url = null;
    this.resource_version = null;
    this.resource_release_date = null;
    this.data_url = null;
    this.data_id = null;
    this.description = null;
  }

  public String getResource_name() {
    return this.resource_name;
  }

  public ExternalDataUnit setResource_name(String resource_name) {
    this.resource_name = resource_name;
    return this;
  }

  public void unsetResource_name() {
    this.resource_name = null;
  }

  /** Returns true if field resource_name is set (has been assigned a value) and false otherwise */
  public boolean isSetResource_name() {
    return this.resource_name != null;
  }

  public void setResource_nameIsSet(boolean value) {
    if (!value) {
      this.resource_name = null;
    }
  }

  public String getResource_url() {
    return this.resource_url;
  }

  public ExternalDataUnit setResource_url(String resource_url) {
    this.resource_url = resource_url;
    return this;
  }

  public void unsetResource_url() {
    this.resource_url = null;
  }

  /** Returns true if field resource_url is set (has been assigned a value) and false otherwise */
  public boolean isSetResource_url() {
    return this.resource_url != null;
  }

  public void setResource_urlIsSet(boolean value) {
    if (!value) {
      this.resource_url = null;
    }
  }

  public String getResource_version() {
    return this.resource_version;
  }

  public ExternalDataUnit setResource_version(String resource_version) {
    this.resource_version = resource_version;
    return this;
  }

  public void unsetResource_version() {
    this.resource_version = null;
  }

  /** Returns true if field resource_version is set (has been assigned a value) and false otherwise */
  public boolean isSetResource_version() {
    return this.resource_version != null;
  }

  public void setResource_versionIsSet(boolean value) {
    if (!value) {
      this.resource_version = null;
    }
  }

  public String getResource_release_date() {
    return this.resource_release_date;
  }

  public ExternalDataUnit setResource_release_date(String resource_release_date) {
    this.resource_release_date = resource_release_date;
    return this;
  }

  public void unsetResource_release_date() {
    this.resource_release_date = null;
  }

  /** Returns true if field resource_release_date is set (has been assigned a value) and false otherwise */
  public boolean isSetResource_release_date() {
    return this.resource_release_date != null;
  }

  public void setResource_release_dateIsSet(boolean value) {
    if (!value) {
      this.resource_release_date = null;
    }
  }

  public String getData_url() {
    return this.data_url;
  }

  public ExternalDataUnit setData_url(String data_url) {
    this.data_url = data_url;
    return this;
  }

  public void unsetData_url() {
    this.data_url = null;
  }

  /** Returns true if field data_url is set (has been assigned a value) and false otherwise */
  public boolean isSetData_url() {
    return this.data_url != null;
  }

  public void setData_urlIsSet(boolean value) {
    if (!value) {
      this.data_url = null;
    }
  }

  public String getData_id() {
    return this.data_id;
  }

  public ExternalDataUnit setData_id(String data_id) {
    this.data_id = data_id;
    return this;
  }

  public void unsetData_id() {
    this.data_id = null;
  }

  /** Returns true if field data_id is set (has been assigned a value) and false otherwise */
  public boolean isSetData_id() {
    return this.data_id != null;
  }

  public void setData_idIsSet(boolean value) {
    if (!value) {
      this.data_id = null;
    }
  }

  public String getDescription() {
    return this.description;
  }

  public ExternalDataUnit setDescription(String description) {
    this.description = description;
    return this;
  }

  public void unsetDescription() {
    this.description = null;
  }

  /** Returns true if field description is set (has been assigned a value) and false otherwise */
  public boolean isSetDescription() {
    return this.description != null;
  }

  public void setDescriptionIsSet(boolean value) {
    if (!value) {
      this.description = null;
    }
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case RESOURCE_NAME:
      if (value == null) {
        unsetResource_name();
      } else {
        setResource_name((String)value);
      }
      break;

    case RESOURCE_URL:
      if (value == null) {
        unsetResource_url();
      } else {
        setResource_url((String)value);
      }
      break;

    case RESOURCE_VERSION:
      if (value == null) {
        unsetResource_version();
      } else {
        setResource_version((String)value);
      }
      break;

    case RESOURCE_RELEASE_DATE:
      if (value == null) {
        unsetResource_release_date();
      } else {
        setResource_release_date((String)value);
      }
      break;

    case DATA_URL:
      if (value == null) {
        unsetData_url();
      } else {
        setData_url((String)value);
      }
      break;

    case DATA_ID:
      if (value == null) {
        unsetData_id();
      } else {
        setData_id((String)value);
      }
      break;

    case DESCRIPTION:
      if (value == null) {
        unsetDescription();
      } else {
        setDescription((String)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case RESOURCE_NAME:
      return getResource_name();

    case RESOURCE_URL:
      return getResource_url();

    case RESOURCE_VERSION:
      return getResource_version();

    case RESOURCE_RELEASE_DATE:
      return getResource_release_date();

    case DATA_URL:
      return getData_url();

    case DATA_ID:
      return getData_id();

    case DESCRIPTION:
      return getDescription();

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case RESOURCE_NAME:
      return isSetResource_name();
    case RESOURCE_URL:
      return isSetResource_url();
    case RESOURCE_VERSION:
      return isSetResource_version();
    case RESOURCE_RELEASE_DATE:
      return isSetResource_release_date();
    case DATA_URL:
      return isSetData_url();
    case DATA_ID:
      return isSetData_id();
    case DESCRIPTION:
      return isSetDescription();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof ExternalDataUnit)
      return this.equals((ExternalDataUnit)that);
    return false;
  }

  public boolean equals(ExternalDataUnit that) {
    if (that == null)
      return false;

    boolean this_present_resource_name = true && this.isSetResource_name();
    boolean that_present_resource_name = true && that.isSetResource_name();
    if (this_present_resource_name || that_present_resource_name) {
      if (!(this_present_resource_name && that_present_resource_name))
        return false;
      if (!this.resource_name.equals(that.resource_name))
        return false;
    }

    boolean this_present_resource_url = true && this.isSetResource_url();
    boolean that_present_resource_url = true && that.isSetResource_url();
    if (this_present_resource_url || that_present_resource_url) {
      if (!(this_present_resource_url && that_present_resource_url))
        return false;
      if (!this.resource_url.equals(that.resource_url))
        return false;
    }

    boolean this_present_resource_version = true && this.isSetResource_version();
    boolean that_present_resource_version = true && that.isSetResource_version();
    if (this_present_resource_version || that_present_resource_version) {
      if (!(this_present_resource_version && that_present_resource_version))
        return false;
      if (!this.resource_version.equals(that.resource_version))
        return false;
    }

    boolean this_present_resource_release_date = true && this.isSetResource_release_date();
    boolean that_present_resource_release_date = true && that.isSetResource_release_date();
    if (this_present_resource_release_date || that_present_resource_release_date) {
      if (!(this_present_resource_release_date && that_present_resource_release_date))
        return false;
      if (!this.resource_release_date.equals(that.resource_release_date))
        return false;
    }

    boolean this_present_data_url = true && this.isSetData_url();
    boolean that_present_data_url = true && that.isSetData_url();
    if (this_present_data_url || that_present_data_url) {
      if (!(this_present_data_url && that_present_data_url))
        return false;
      if (!this.data_url.equals(that.data_url))
        return false;
    }

    boolean this_present_data_id = true && this.isSetData_id();
    boolean that_present_data_id = true && that.isSetData_id();
    if (this_present_data_id || that_present_data_id) {
      if (!(this_present_data_id && that_present_data_id))
        return false;
      if (!this.data_id.equals(that.data_id))
        return false;
    }

    boolean this_present_description = true && this.isSetDescription();
    boolean that_present_description = true && that.isSetDescription();
    if (this_present_description || that_present_description) {
      if (!(this_present_description && that_present_description))
        return false;
      if (!this.description.equals(that.description))
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    List<Object> list = new ArrayList<Object>();

    boolean present_resource_name = true && (isSetResource_name());
    list.add(present_resource_name);
    if (present_resource_name)
      list.add(resource_name);

    boolean present_resource_url = true && (isSetResource_url());
    list.add(present_resource_url);
    if (present_resource_url)
      list.add(resource_url);

    boolean present_resource_version = true && (isSetResource_version());
    list.add(present_resource_version);
    if (present_resource_version)
      list.add(resource_version);

    boolean present_resource_release_date = true && (isSetResource_release_date());
    list.add(present_resource_release_date);
    if (present_resource_release_date)
      list.add(resource_release_date);

    boolean present_data_url = true && (isSetData_url());
    list.add(present_data_url);
    if (present_data_url)
      list.add(data_url);

    boolean present_data_id = true && (isSetData_id());
    list.add(present_data_id);
    if (present_data_id)
      list.add(data_id);

    boolean present_description = true && (isSetDescription());
    list.add(present_description);
    if (present_description)
      list.add(description);

    return list.hashCode();
  }

  @Override
  public int compareTo(ExternalDataUnit other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;

    lastComparison = Boolean.valueOf(isSetResource_name()).compareTo(other.isSetResource_name());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetResource_name()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.resource_name, other.resource_name);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetResource_url()).compareTo(other.isSetResource_url());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetResource_url()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.resource_url, other.resource_url);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetResource_version()).compareTo(other.isSetResource_version());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetResource_version()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.resource_version, other.resource_version);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetResource_release_date()).compareTo(other.isSetResource_release_date());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetResource_release_date()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.resource_release_date, other.resource_release_date);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetData_url()).compareTo(other.isSetData_url());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetData_url()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.data_url, other.data_url);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetData_id()).compareTo(other.isSetData_id());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetData_id()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.data_id, other.data_id);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetDescription()).compareTo(other.isSetDescription());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetDescription()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.description, other.description);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    return 0;
  }

  public _Fields fieldForId(int fieldId) {
    return _Fields.findByThriftId(fieldId);
  }

  public void read(org.apache.thrift.protocol.TProtocol iprot) throws org.apache.thrift.TException {
    schemes.get(iprot.getScheme()).getScheme().read(iprot, this);
  }

  public void write(org.apache.thrift.protocol.TProtocol oprot) throws org.apache.thrift.TException {
    schemes.get(oprot.getScheme()).getScheme().write(oprot, this);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder("ExternalDataUnit(");
    boolean first = true;

    sb.append("resource_name:");
    if (this.resource_name == null) {
      sb.append("null");
    } else {
      sb.append(this.resource_name);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("resource_url:");
    if (this.resource_url == null) {
      sb.append("null");
    } else {
      sb.append(this.resource_url);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("resource_version:");
    if (this.resource_version == null) {
      sb.append("null");
    } else {
      sb.append(this.resource_version);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("resource_release_date:");
    if (this.resource_release_date == null) {
      sb.append("null");
    } else {
      sb.append(this.resource_release_date);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("data_url:");
    if (this.data_url == null) {
      sb.append("null");
    } else {
      sb.append(this.data_url);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("data_id:");
    if (this.data_id == null) {
      sb.append("null");
    } else {
      sb.append(this.data_id);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("description:");
    if (this.description == null) {
      sb.append("null");
    } else {
      sb.append(this.description);
    }
    first = false;
    sb.append(")");
    return sb.toString();
  }

  public void validate() throws org.apache.thrift.TException {
    // check for required fields
    // check for sub-struct validity
  }

  private void writeObject(java.io.ObjectOutputStream out) throws java.io.IOException {
    try {
      write(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(out)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private void readObject(java.io.ObjectInputStream in) throws java.io.IOException, ClassNotFoundException {
    try {
      read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private static class ExternalDataUnitStandardSchemeFactory implements SchemeFactory {
    public ExternalDataUnitStandardScheme getScheme() {
      return new ExternalDataUnitStandardScheme();
    }
  }

  private static class ExternalDataUnitStandardScheme extends StandardScheme<ExternalDataUnit> {

    public void read(org.apache.thrift.protocol.TProtocol iprot, ExternalDataUnit struct) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField schemeField;
      iprot.readStructBegin();
      while (true)
      {
        schemeField = iprot.readFieldBegin();
        if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (schemeField.id) {
          case 1: // RESOURCE_NAME
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.resource_name = iprot.readString();
              struct.setResource_nameIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 2: // RESOURCE_URL
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.resource_url = iprot.readString();
              struct.setResource_urlIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 3: // RESOURCE_VERSION
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.resource_version = iprot.readString();
              struct.setResource_versionIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 4: // RESOURCE_RELEASE_DATE
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.resource_release_date = iprot.readString();
              struct.setResource_release_dateIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 5: // DATA_URL
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.data_url = iprot.readString();
              struct.setData_urlIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 6: // DATA_ID
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.data_id = iprot.readString();
              struct.setData_idIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 7: // DESCRIPTION
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.description = iprot.readString();
              struct.setDescriptionIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          default:
            org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
        }
        iprot.readFieldEnd();
      }
      iprot.readStructEnd();

      // check for required fields of primitive type, which can't be checked in the validate method
      struct.validate();
    }

    public void write(org.apache.thrift.protocol.TProtocol oprot, ExternalDataUnit struct) throws org.apache.thrift.TException {
      struct.validate();

      oprot.writeStructBegin(STRUCT_DESC);
      if (struct.resource_name != null) {
        oprot.writeFieldBegin(RESOURCE_NAME_FIELD_DESC);
        oprot.writeString(struct.resource_name);
        oprot.writeFieldEnd();
      }
      if (struct.resource_url != null) {
        oprot.writeFieldBegin(RESOURCE_URL_FIELD_DESC);
        oprot.writeString(struct.resource_url);
        oprot.writeFieldEnd();
      }
      if (struct.resource_version != null) {
        oprot.writeFieldBegin(RESOURCE_VERSION_FIELD_DESC);
        oprot.writeString(struct.resource_version);
        oprot.writeFieldEnd();
      }
      if (struct.resource_release_date != null) {
        oprot.writeFieldBegin(RESOURCE_RELEASE_DATE_FIELD_DESC);
        oprot.writeString(struct.resource_release_date);
        oprot.writeFieldEnd();
      }
      if (struct.data_url != null) {
        oprot.writeFieldBegin(DATA_URL_FIELD_DESC);
        oprot.writeString(struct.data_url);
        oprot.writeFieldEnd();
      }
      if (struct.data_id != null) {
        oprot.writeFieldBegin(DATA_ID_FIELD_DESC);
        oprot.writeString(struct.data_id);
        oprot.writeFieldEnd();
      }
      if (struct.description != null) {
        oprot.writeFieldBegin(DESCRIPTION_FIELD_DESC);
        oprot.writeString(struct.description);
        oprot.writeFieldEnd();
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

  }

  private static class ExternalDataUnitTupleSchemeFactory implements SchemeFactory {
    public ExternalDataUnitTupleScheme getScheme() {
      return new ExternalDataUnitTupleScheme();
    }
  }

  private static class ExternalDataUnitTupleScheme extends TupleScheme<ExternalDataUnit> {

    @Override
    public void write(org.apache.thrift.protocol.TProtocol prot, ExternalDataUnit struct) throws org.apache.thrift.TException {
      TTupleProtocol oprot = (TTupleProtocol) prot;
      BitSet optionals = new BitSet();
      if (struct.isSetResource_name()) {
        optionals.set(0);
      }
      if (struct.isSetResource_url()) {
        optionals.set(1);
      }
      if (struct.isSetResource_version()) {
        optionals.set(2);
      }
      if (struct.isSetResource_release_date()) {
        optionals.set(3);
      }
      if (struct.isSetData_url()) {
        optionals.set(4);
      }
      if (struct.isSetData_id()) {
        optionals.set(5);
      }
      if (struct.isSetDescription()) {
        optionals.set(6);
      }
      oprot.writeBitSet(optionals, 7);
      if (struct.isSetResource_name()) {
        oprot.writeString(struct.resource_name);
      }
      if (struct.isSetResource_url()) {
        oprot.writeString(struct.resource_url);
      }
      if (struct.isSetResource_version()) {
        oprot.writeString(struct.resource_version);
      }
      if (struct.isSetResource_release_date()) {
        oprot.writeString(struct.resource_release_date);
      }
      if (struct.isSetData_url()) {
        oprot.writeString(struct.data_url);
      }
      if (struct.isSetData_id()) {
        oprot.writeString(struct.data_id);
      }
      if (struct.isSetDescription()) {
        oprot.writeString(struct.description);
      }
    }

    @Override
    public void read(org.apache.thrift.protocol.TProtocol prot, ExternalDataUnit struct) throws org.apache.thrift.TException {
      TTupleProtocol iprot = (TTupleProtocol) prot;
      BitSet incoming = iprot.readBitSet(7);
      if (incoming.get(0)) {
        struct.resource_name = iprot.readString();
        struct.setResource_nameIsSet(true);
      }
      if (incoming.get(1)) {
        struct.resource_url = iprot.readString();
        struct.setResource_urlIsSet(true);
      }
      if (incoming.get(2)) {
        struct.resource_version = iprot.readString();
        struct.setResource_versionIsSet(true);
      }
      if (incoming.get(3)) {
        struct.resource_release_date = iprot.readString();
        struct.setResource_release_dateIsSet(true);
      }
      if (incoming.get(4)) {
        struct.data_url = iprot.readString();
        struct.setData_urlIsSet(true);
      }
      if (incoming.get(5)) {
        struct.data_id = iprot.readString();
        struct.setData_idIsSet(true);
      }
      if (incoming.get(6)) {
        struct.description = iprot.readString();
        struct.setDescriptionIsSet(true);
      }
    }
  }

}
