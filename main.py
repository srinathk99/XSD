from OpenAI.openaiClient import generate_sample_from_skeleton,generate_xml_from_xsd,xml_with_validation_error_regenerate
from xsd import validate_xml_using_xsd_sxhema
from technique.find_schema import detect_matching_schema,detect_best_matching_schema

if __name__ == '__main__':
    xsd_path = "resource/CstmrCdtTrfTraceFormat.xsd"
    ske_paath="CstmrCdtTrfTraceFormat_skeleton.xml"

    sample=generate_sample_from_skeleton(ske_paath,xsd_path)
    print(sample)
    print("finished")

    # matches, errors = detect_matching_schema("input.xml")
    #
    # if len(matches) == 1:
    #     print("✅ Matched schema:", matches[0])
    #
    # elif len(matches) > 1:
    #     print("⚠️ Ambiguous match:", matches)
    #
    # else:
    #     print("❌ No schema matched")
    #     best, all_results = detect_best_matching_schema("input.xml", threshold=90)
    #
    #     if best:
    #         print(f"✅ Best match: {best['schema']} ({best['score']}%)")
    #     else:
    #         print("❌ No schema matched above threshold")
    #
    #     print("\nAll candidates:")
    #     for r in all_results:
    #         print(f"{r['schema']} → {r['score']}% (errors={r['errors']})")

    # xml_sample = generate_xml_from_xsd(xsd_path)
    # print(xml_sample)
    # res=validate_xml_using_xsd_sxhema(xsd_path,xml_sample)
    # print(res)
    # count=0
    # while res!= "success":
    #
    #     count=count+1
    #     print(count)
    #     xml_sample = xml_with_validation_error_regenerate(xml_sample,res)
    #     print(xml_sample)
    #     res = validate_xml_using_xsd_sxhema(xsd_path, xml_sample)
    #     print(res)
    #     count+=1
    #
    #
    # print(xml_sample)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
