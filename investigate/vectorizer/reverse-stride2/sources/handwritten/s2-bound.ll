; Hand-written (make_s2_bound.py). One stride-2 loop with one in-loop check; only the bound's expression and the
; flags of the shift differ between the functions. See the docstring of make_s2_bound.py.
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

declare void @llvm.trap() #0
declare i64 @llvm.umax.i64(i64, i64)
declare i64 @llvm.umin.i64(i64, i64)
attributes #0 = { cold noreturn nounwind }

define void @f_full_plain(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = add i64 %an, 0
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_ashr2_plain(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = ashr i64 %an, 2
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_lshr1_plain(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = lshr i64 %an, 1
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_and62_plain(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = and i64 %an, 4611686018427387903
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_umin40_plain(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = call i64 @llvm.umin.i64(i64 %an, i64 1099511627776)
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_ptr_ashr_plain(ptr noalias %c, ptr noalias %a, i64 %n, ptr %beg, ptr %end) {
entry:
  %pe = ptrtoint ptr %end to i64
  %pb = ptrtoint ptr %beg to i64
  %bytes = sub i64 %pe, %pb
  %bound = ashr exact i64 %bytes, 2
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_ptr_lshr_plain(ptr noalias %c, ptr noalias %a, i64 %n, ptr %beg, ptr %end) {
entry:
  %pe = ptrtoint ptr %end to i64
  %pb = ptrtoint ptr %beg to i64
  %bytes = sub i64 %pe, %pb
  %bound = lshr exact i64 %bytes, 1
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_full_nuw(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = add i64 %an, 0
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_ashr2_nuw(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = ashr i64 %an, 2
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_lshr1_nuw(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = lshr i64 %an, 1
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_and62_nuw(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = and i64 %an, 4611686018427387903
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_umin40_nuw(ptr noalias %c, ptr noalias %a, i64 %n, i64 %an) {
entry:
  %bound = call i64 @llvm.umin.i64(i64 %an, i64 1099511627776)
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_ptr_ashr_nuw(ptr noalias %c, ptr noalias %a, i64 %n, ptr %beg, ptr %end) {
entry:
  %pe = ptrtoint ptr %end to i64
  %pb = ptrtoint ptr %beg to i64
  %bytes = sub i64 %pe, %pb
  %bound = ashr exact i64 %bytes, 2
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}

define void @f_ptr_lshr_nuw(ptr noalias %c, ptr noalias %a, i64 %n, ptr %beg, ptr %end) {
entry:
  %pe = ptrtoint ptr %end to i64
  %pb = ptrtoint ptr %beg to i64
  %bytes = sub i64 %pe, %pb
  %bound = lshr exact i64 %bytes, 1
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl nuw i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}
