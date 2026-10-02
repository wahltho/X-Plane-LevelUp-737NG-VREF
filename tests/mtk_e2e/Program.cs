using System.Security.Cryptography;
using System.Text.Json;
using LevelUp.NavTableUpdater.Core.Aircraft;
using LevelUp.NavTableUpdater.Core.Content;
using LevelUp.NavTableUpdater.Core.State;
var root=Path.GetFullPath(args[0]);
var fixturesRoot=Path.Combine(root,"artifacts/mtk-preview3-fixtures");
using var fixtures=JsonDocument.Parse(File.ReadAllText(Path.Combine(fixturesRoot,"fixtures.json")));
var cases=fixtures.RootElement.GetProperty("cases").EnumerateArray().ToArray();
var packages=Path.Combine(root,"artifacts/mtk-e2e-packages");
var temporary=Path.Combine(Path.GetTempPath(),"vref-mtk-e2e-"+Guid.NewGuid());Directory.CreateDirectory(temporary);
byte[] Read(JsonElement x)=>File.ReadAllBytes(Path.Combine(fixturesRoot,x.GetProperty("path").GetString()!));
void Require(bool ok,string message){if(!ok)throw new Exception(message);}
Dictionary<string,string> Snapshot(string dir)=>Directory.GetFiles(dir,"*",SearchOption.AllDirectories).ToDictionary(x=>Path.GetRelativePath(dir,x),x=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(x))));
void EqualSnapshots(Dictionary<string,string> before,Dictionary<string,string> after,string label)=>Require(before.Count==after.Count && before.All(x=>after.TryGetValue(x.Key,out var value)&&value==x.Value),"Blocked mutation: "+label);
int positive=0,blocked=0;
try
{
 foreach(var family in new[]{"LevelUp","Zibo"})
 foreach(var mode in new[]{"fresh","preview1","preview2","preview3","preview1-composed","preview2-composed","preview3-composed"})
 {
  if(family=="Zibo" && mode.StartsWith("preview1"))continue; // Released preview1 supports LevelUp only.
  var testRoot=Path.Combine(temporary,family+"-"+mode);var aircraft=Path.Combine(testRoot,"aircraft");Directory.CreateDirectory(aircraft);
  var acf=Path.Combine(aircraft,family=="Zibo"?"b738.acf":"737_70NG.acf");File.WriteAllText(acf,"1200 Version\n");
  var variant=new AircraftVariantViewAnalysis(family=="Zibo"?"zibo-737-800":"levelup-737-700",family,family,acf,Path.ChangeExtension(acf,null)+"_prefs.txt","test","test",family=="Zibo"?"4.05.35":"V2.S1.50",family=="Zibo"?"4.05.35":"V2.S1.50",null,null,null,null,0,0,null,null,null,null,"test","test","test","test");
  var store=new ToolStateStore(Path.Combine(testRoot,"state"),Path.Combine(testRoot,"backups"));
  var operation=new CompatibilityPackageOperation(store,()=>false);
  var freshCases=cases.Where(x=>x.GetProperty("id").GetString()!.EndsWith("/fresh")).ToArray();
  foreach(var item in freshCases){var path=Path.Combine(aircraft,item.GetProperty("scriptPath").GetString()!);Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllBytes(path,Read(item.GetProperty("input")));}
  var current=Path.Combine(packages,"current");
  if(mode!="fresh")
  {
   var oldLabel=mode.Split('-')[0];
   var oldInstall=await operation.RunAsync(ContentPatchAction.Install,variant,Path.Combine(packages,oldLabel),["vref"]);
   Require(oldInstall.Succeeded,family+" "+mode+" seed: "+oldInstall.Message);
   foreach(var item in cases.Where(x=>x.GetProperty("id").GetString()!.EndsWith("/"+oldLabel+"-upgrade")))
   {Require(File.ReadAllBytes(Path.Combine(aircraft,item.GetProperty("scriptPath").GetString()!)).SequenceEqual(Read(item.GetProperty("input"))),"Old seed mismatch");}
   if(mode.EndsWith("composed"))
    foreach(var item in cases.Where(x=>x.GetProperty("id").GetString()!.EndsWith("/"+oldLabel+"-composed-upgrade")))File.WriteAllBytes(Path.Combine(aircraft,item.GetProperty("scriptPath").GetString()!),Read(item.GetProperty("input")));
  }
  var before=Snapshot(testRoot);
  var result=await operation.RunAsync(mode=="fresh"?ContentPatchAction.Install:ContentPatchAction.Update,variant,current,["vref"]);
  if(mode.EndsWith("composed"))
  {
   Require(!result.Succeeded,"Composed update unexpectedly succeeded");EqualSnapshots(before,Snapshot(testRoot),mode);blocked++;Console.WriteLine($"{family}/{mode}: safely BLOCKED, all aircraft/state/backup bytes unchanged");continue;
  }
  Require(result.Succeeded,family+" "+mode+": "+result.Message);
  foreach(var item in freshCases)
  {
   Require(File.ReadAllBytes(Path.Combine(aircraft,item.GetProperty("scriptPath").GetString()!)).SequenceEqual(Read(item.GetProperty("expected"))),"Installed script mismatch");
   Require(File.ReadAllBytes(Path.Combine(aircraft,item.GetProperty("modulePath").GetString()!)).SequenceEqual(Read(item.GetProperty("moduleAfter"))),"Installed module mismatch");
  }
  Require((await operation.RunAsync(ContentPatchAction.Update,variant,current,["vref"])).Succeeded,"Repeat failed");
  var restore=operation.Restore(variant,current);Require(restore.Succeeded,"Restore failed: "+restore.Message);
  foreach(var item in freshCases){Require(File.ReadAllBytes(Path.Combine(aircraft,item.GetProperty("scriptPath").GetString()!)).SequenceEqual(Read(item.GetProperty("input"))),"Restore script mismatch");Require(!File.Exists(Path.Combine(aircraft,item.GetProperty("modulePath").GetString()!)),"Restore left module");}
  positive++;Console.WriteLine($"{family}/{mode}: install/update, repeat, complete Restore PASS");
 }
 var corruptBlocked=0;
 foreach(var bad in cases.Where(x=>x.GetProperty("mustBlockWithoutAnyWrites").GetBoolean()))
 {
  var testRoot=Path.Combine(temporary,"corrupt-"+corruptBlocked);var aircraft=Path.Combine(testRoot,"aircraft");Directory.CreateDirectory(aircraft);
  var acf=Path.Combine(aircraft,"737_70NG.acf");File.WriteAllText(acf,"1200 Version\n");
  var variant=new AircraftVariantViewAnalysis("levelup-737-700","LevelUp","LevelUp",acf,Path.ChangeExtension(acf,null)+"_prefs.txt","test","test","V2.S1.50","V2.S1.50",null,null,null,null,0,0,null,null,null,null,"test","test","test","test");
  var store=new ToolStateStore(Path.Combine(testRoot,"state"),Path.Combine(testRoot,"backups"));var operation=new CompatibilityPackageOperation(store,()=>false);
  foreach(var clean in cases.Where(x=>x.GetProperty("id").GetString()!.EndsWith("/fresh")))
  {var path=Path.Combine(aircraft,clean.GetProperty("scriptPath").GetString()!);Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllBytes(path,Read(clean.GetProperty("input")));}
  File.WriteAllBytes(Path.Combine(aircraft,bad.GetProperty("scriptPath").GetString()!),Read(bad.GetProperty("input")));
  var before=Snapshot(testRoot);
  var result=await operation.RunAsync(ContentPatchAction.Install,variant,Path.Combine(packages,"current"),["vref"]);
  Require(!result.Succeeded,"Corrupt marker accepted: "+bad.GetProperty("id").GetString());EqualSnapshots(before,Snapshot(testRoot),bad.GetProperty("id").GetString()!);corruptBlocked++;
 }
 Console.WriteLine($"Real MTK E2E: {corruptBlocked} corrupt-marker cases BLOCKED with all target/state/backup bytes unchanged.");
 Console.WriteLine($"Real MTK E2E: {positive} lifecycle scenarios PASS; {blocked} composed scenarios safely BLOCKED. No simulator.");
}
finally{Directory.Delete(temporary,true);}
