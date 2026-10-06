package main

import (
	"fmt"
	"regexp"
	"strings"
	"time"
	"unsafe"

	"github.com/valyala/fastjson"
)

//export filter_error_log
func filter_error_log(tag *uint8, tag_len uint, time_sec uint, time_nsec uint, record *uint8, record_len uint) *uint8 {
	var deadlockStrings = []string{
		"WE ROLL BACK TRANSACTION",
		"CONFLICTING WITH",
		"LOCK WAIT",
		"WAITING FOR THIS LOCK",
		"deadlock detected",
	}

	oldRecord := unsafe.Slice(record, record_len)
	oldRecordStr := string(oldRecord)

	var parser fastjson.Parser
	value, err := parser.Parse(oldRecordStr)
	if err != nil {
		fmt.Println(err)
		return nil
	}

	obj, err := value.Object()
	if err != nil {
		fmt.Println(err)
		return nil
	}

	var arena fastjson.Arena

	errorMsg := obj.Get("log").String()

	errorRe := regexp.MustCompile(`[0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s[0-9]+\s\[.*\]`)
	errorMatch := errorRe.FindString(errorMsg)
	errorTags := strings.Split(errorMatch, " ")
	if len(errorTags) >= 4 {
		// Parser error log date time as time
		t, err := time.Parse("2006-01-02 15:04:05", errorTags[0]+" "+errorTags[1])
		if err == nil {
			obj.Set("time", arena.NewString(t.String()))
		}

		obj.Set("thread_id", arena.NewString(errorTags[2]))

		level := strings.TrimPrefix(errorTags[3], "[")
		level = strings.TrimSuffix(level, "]")
		obj.Set("level", arena.NewString(level))
	}
	for _, d := range deadlockStrings {
		if strings.Contains(errorMsg, d) {
			obj.Set("deadlock", arena.NewTrue())
			continue
		}
	}

	newRecord := obj.String()
	newRecord += string(rune(0))
	recordValue := []byte(newRecord)

	return &recordValue[0]

}

func main() {}
