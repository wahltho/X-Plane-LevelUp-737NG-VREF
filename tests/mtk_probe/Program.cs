using System.Security.Cryptography;
using System.Text.Json;
using LevelUp.NavTableUpdater.Core.Content.PatchHandlers;
var root = Path.GetFullPath(args[0]);
var fixturePath = args.Length > 1 ? Path.GetFullPath(args[1]) : Path.Combine(root,"artifacts/mtk-preview3-fixtures/fixtures.json");
var fixtureRoot = Path.GetDirectoryName(fixturePath)!;
using var fixtures = JsonDocument.Parse(File.ReadAllText(fixturePath));
using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"package-manifest.json")));
var handlers = new IContentPatchHandler[]{new ExactTextReplacementsPatchHandler(),new MarkedBlockInsertionPatchHandler(),new MarkedBlockMigrationPatchHandler()}.ToDictionary(x=>x.Operation);
byte[] ReadFixture(JsonElement descriptor)
{
 var bytes = File.ReadAllBytes(Path.Combine(fixtureRoot,descriptor.GetProperty("path").GetString()!));
 if(bytes.Length != descriptor.GetProperty("size").GetInt32() || !Convert.ToHexString(SHA256.HashData(bytes)).Equals(descriptor.GetProperty("sha256").GetString(),StringComparison.OrdinalIgnoreCase))throw new Exception("Fixture hash/size mismatch");
 return bytes;
}
byte[] Apply(byte[] source,string scriptPath)
{
 var result=source;
 foreach(var operation in manifest.RootElement.GetProperty("modules")[0].GetProperty("targets").EnumerateArray().Where(x=>x.GetProperty("relativePath").GetString()==scriptPath))
 {
  var payloadName=operation.GetProperty("payload").GetString()!;
  var bytes=File.ReadAllBytes(Path.Combine(root,payloadName));
  var metadata=manifest.RootElement.GetProperty("modules")[0].GetProperty("payloads").EnumerateArray().Single(x=>x.GetProperty("path").GetString()==payloadName);
  if(bytes.Length!=metadata.GetProperty("size").GetInt32() || !Convert.ToHexString(SHA256.HashData(bytes)).Equals(metadata.GetProperty("sha256").GetString(),StringComparison.OrdinalIgnoreCase))throw new Exception("Payload integrity mismatch");
  using var payload=JsonDocument.Parse(bytes);
  result=handlers[operation.GetProperty("operation").GetString()!].Apply(result,payload.RootElement);
 }
 return result;
}
var passed=0;var blocked=0;
foreach(var item in fixtures.RootElement.GetProperty("cases").EnumerateArray())
{
 var id=item.GetProperty("id").GetString();
 var source=ReadFixture(item.GetProperty("input"));
 var scriptPath=item.GetProperty("scriptPath").GetString()!;
 if(item.GetProperty("mustBlockWithoutAnyWrites").GetBoolean())
 {
  var rejected=false;try{Apply(source,scriptPath);}catch(InvalidOperationException){rejected=true;}
  if(!rejected)throw new Exception("Invalid source was accepted: "+id);
  blocked++;
 }
 else
 {
  var actual=Apply(source,scriptPath);
  if(!actual.SequenceEqual(ReadFixture(item.GetProperty("expected"))))throw new Exception("Output differs: "+id);
  if(!Apply(actual,scriptPath).SequenceEqual(actual))throw new Exception("Repeat differs: "+id);
  passed++;
 }
}
Console.WriteLine($"Production handlers with generated VREF payloads: {passed} install/upgrade + repeat cases PASS; {blocked} corrupt-marker cases correctly BLOCKED.");
Console.WriteLine("No MTK planner, copy transaction, ownership persistence or Restore executed: end-to-end gate remains open.");
namespace LevelUp.NavTableUpdater.Core.Content.PatchHandlers
{
 // Only this interface is a test shell; all handler/codec/JSON sources are linked unchanged.
 public interface IContentPatchHandler { string Operation {get;} bool SupportsStructuralSourceValidation {get;} byte[] Apply(byte[] source,JsonElement payload); }
}
