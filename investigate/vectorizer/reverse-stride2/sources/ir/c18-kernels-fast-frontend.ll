; ModuleID = '/app/example.cpp'
source_filename = "/app/example.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%"class.std::__1::vector" = type { ptr, ptr, %"class.std::__1::__compressed_pair" }
%"class.std::__1::__compressed_pair" = type { %"struct.std::__1::__compressed_pair_elem" }
%"struct.std::__1::__compressed_pair_elem" = type { ptr }

$_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev = comdat any

$_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em = comdat any

$_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em = comdat any

@.str = private unnamed_addr constant [170 x i8] c"/cefs/d2/d2e6ebb9fe16525f6e7eb0c3_consolidated/compilers_c++_clang_18.1.0/bin/../include/c++/v1/vector:1400: assertion __n < size() failed: vector[] index out of bounds\0A\00", align 1
@.str.1 = private unnamed_addr constant [170 x i8] c"/cefs/d2/d2e6ebb9fe16525f6e7eb0c3_consolidated/compilers_c++_clang_18.1.0/bin/../include/c++/v1/vector:1393: assertion __n < size() failed: vector[] index out of bounds\0A\00", align 1

; Function Attrs: mustprogress noinline nounwind uwtable
define dso_local noundef i64 @_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE(ptr noundef nonnull align 8 dereferenceable(24) %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca i64, align 8
  %4 = alloca i64, align 8
  store ptr %0, ptr %2, align 8, !tbaa !5
  call void @llvm.lifetime.start.p0(i64 8, ptr %3) #6
  store i64 0, ptr %3, align 8, !tbaa !9
  call void @llvm.lifetime.start.p0(i64 8, ptr %4) #6
  store i64 0, ptr %4, align 8, !tbaa !9
  br label %5

5:                                                ; preds = %19, %1
  %6 = load i64, ptr %4, align 8, !tbaa !9
  %7 = load ptr, ptr %2, align 8, !tbaa !5
  %8 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %7) #6
  %9 = icmp ult i64 %6, %8
  br i1 %9, label %11, label %10

10:                                               ; preds = %5
  call void @llvm.lifetime.end.p0(i64 8, ptr %4) #6
  br label %22

11:                                               ; preds = %5
  %12 = load ptr, ptr %2, align 8, !tbaa !5
  %13 = load i64, ptr %4, align 8, !tbaa !9
  %14 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %12, i64 noundef %13) #6
  %15 = load i32, ptr %14, align 4, !tbaa !11
  %16 = sext i32 %15 to i64
  %17 = load i64, ptr %3, align 8, !tbaa !9
  %18 = add nsw i64 %17, %16
  store i64 %18, ptr %3, align 8, !tbaa !9
  br label %19

19:                                               ; preds = %11
  %20 = load i64, ptr %4, align 8, !tbaa !9
  %21 = add i64 %20, 1
  store i64 %21, ptr %4, align 8, !tbaa !9
  br label %5, !llvm.loop !13

22:                                               ; preds = %10
  %23 = load i64, ptr %3, align 8, !tbaa !9
  call void @llvm.lifetime.end.p0(i64 8, ptr %3) #6
  ret i64 %23
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress nounwind uwtable
define linkonce_odr hidden noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %0) #2 comdat align 2 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8, !tbaa !5
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %"class.std::__1::vector", ptr %3, i32 0, i32 1
  %5 = load ptr, ptr %4, align 8, !tbaa !15
  %6 = getelementptr inbounds %"class.std::__1::vector", ptr %3, i32 0, i32 0
  %7 = load ptr, ptr %6, align 8, !tbaa !19
  %8 = ptrtoint ptr %5 to i64
  %9 = ptrtoint ptr %7 to i64
  %10 = sub i64 %8, %9
  %11 = sdiv exact i64 %10, 4
  ret i64 %11
}

; Function Attrs: inlinehint mustprogress nounwind uwtable
define linkonce_odr hidden noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %0, i64 noundef %1) #3 comdat align 2 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  store ptr %0, ptr %3, align 8, !tbaa !5
  store i64 %1, ptr %4, align 8, !tbaa !9
  %5 = load ptr, ptr %3, align 8
  %6 = load i64, ptr %4, align 8, !tbaa !9
  %7 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %5) #6
  %8 = icmp ult i64 %6, %7
  %9 = zext i1 %8 to i64
  %10 = call i64 @llvm.expect.i64(i64 %9, i64 1)
  %11 = icmp ne i64 %10, 0
  br i1 %11, label %12, label %13

12:                                               ; preds = %2
  br label %14

13:                                               ; preds = %2
  call void @llvm.trap()
  br label %14

14:                                               ; preds = %13, %12
  %15 = getelementptr inbounds %"class.std::__1::vector", ptr %5, i32 0, i32 0
  %16 = load ptr, ptr %15, align 8, !tbaa !19
  %17 = load i64, ptr %4, align 8, !tbaa !9
  %18 = getelementptr inbounds i32, ptr %16, i64 %17
  ret ptr %18
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress noinline nounwind uwtable
define dso_local void @_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_(ptr noundef nonnull align 8 dereferenceable(24) %0, ptr noundef nonnull align 8 dereferenceable(24) %1, ptr noundef nonnull align 8 dereferenceable(24) %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  store ptr %0, ptr %4, align 8, !tbaa !5
  store ptr %1, ptr %5, align 8, !tbaa !5
  store ptr %2, ptr %6, align 8, !tbaa !5
  call void @llvm.lifetime.start.p0(i64 8, ptr %7) #6
  store i64 0, ptr %7, align 8, !tbaa !9
  br label %8

8:                                                ; preds = %27, %3
  %9 = load i64, ptr %7, align 8, !tbaa !9
  %10 = load ptr, ptr %5, align 8, !tbaa !5
  %11 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %10) #6
  %12 = icmp ult i64 %9, %11
  br i1 %12, label %14, label %13

13:                                               ; preds = %8
  call void @llvm.lifetime.end.p0(i64 8, ptr %7) #6
  br label %30

14:                                               ; preds = %8
  %15 = load ptr, ptr %5, align 8, !tbaa !5
  %16 = load i64, ptr %7, align 8, !tbaa !9
  %17 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %15, i64 noundef %16) #6
  %18 = load i32, ptr %17, align 4, !tbaa !11
  %19 = load ptr, ptr %6, align 8, !tbaa !5
  %20 = load i64, ptr %7, align 8, !tbaa !9
  %21 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %19, i64 noundef %20) #6
  %22 = load i32, ptr %21, align 4, !tbaa !11
  %23 = add nsw i32 %18, %22
  %24 = load ptr, ptr %4, align 8, !tbaa !5
  %25 = load i64, ptr %7, align 8, !tbaa !9
  %26 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %24, i64 noundef %25) #6
  store i32 %23, ptr %26, align 4, !tbaa !11
  br label %27

27:                                               ; preds = %14
  %28 = load i64, ptr %7, align 8, !tbaa !9
  %29 = add i64 %28, 1
  store i64 %29, ptr %7, align 8, !tbaa !9
  br label %8, !llvm.loop !20

30:                                               ; preds = %13
  ret void
}

; Function Attrs: inlinehint mustprogress nounwind uwtable
define linkonce_odr hidden noundef nonnull align 4 dereferenceable(4) ptr @_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %0, i64 noundef %1) #3 comdat align 2 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  store ptr %0, ptr %3, align 8, !tbaa !5
  store i64 %1, ptr %4, align 8, !tbaa !9
  %5 = load ptr, ptr %3, align 8
  %6 = load i64, ptr %4, align 8, !tbaa !9
  %7 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %5) #6
  %8 = icmp ult i64 %6, %7
  %9 = zext i1 %8 to i64
  %10 = call i64 @llvm.expect.i64(i64 %9, i64 1)
  %11 = icmp ne i64 %10, 0
  br i1 %11, label %12, label %13

12:                                               ; preds = %2
  br label %14

13:                                               ; preds = %2
  call void @llvm.trap()
  br label %14

14:                                               ; preds = %13, %12
  %15 = getelementptr inbounds %"class.std::__1::vector", ptr %5, i32 0, i32 0
  %16 = load ptr, ptr %15, align 8, !tbaa !19
  %17 = load i64, ptr %4, align 8, !tbaa !9
  %18 = getelementptr inbounds i32, ptr %16, i64 %17
  ret ptr %18
}

; Function Attrs: mustprogress noinline nounwind uwtable
define dso_local void @_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr noundef nonnull align 8 dereferenceable(24) %0, ptr noundef nonnull align 8 dereferenceable(24) %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  store ptr %0, ptr %3, align 8, !tbaa !5
  store ptr %1, ptr %4, align 8, !tbaa !5
  call void @llvm.lifetime.start.p0(i64 8, ptr %5) #6
  store i64 1, ptr %5, align 8, !tbaa !9
  br label %6

6:                                                ; preds = %33, %2
  %7 = load i64, ptr %5, align 8, !tbaa !9
  %8 = add i64 %7, 1
  %9 = load ptr, ptr %4, align 8, !tbaa !5
  %10 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %9) #6
  %11 = icmp ult i64 %8, %10
  br i1 %11, label %13, label %12

12:                                               ; preds = %6
  call void @llvm.lifetime.end.p0(i64 8, ptr %5) #6
  br label %36

13:                                               ; preds = %6
  %14 = load ptr, ptr %4, align 8, !tbaa !5
  %15 = load i64, ptr %5, align 8, !tbaa !9
  %16 = sub i64 %15, 1
  %17 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %14, i64 noundef %16) #6
  %18 = load i32, ptr %17, align 4, !tbaa !11
  %19 = load ptr, ptr %4, align 8, !tbaa !5
  %20 = load i64, ptr %5, align 8, !tbaa !9
  %21 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %19, i64 noundef %20) #6
  %22 = load i32, ptr %21, align 4, !tbaa !11
  %23 = add nsw i32 %18, %22
  %24 = load ptr, ptr %4, align 8, !tbaa !5
  %25 = load i64, ptr %5, align 8, !tbaa !9
  %26 = add i64 %25, 1
  %27 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %24, i64 noundef %26) #6
  %28 = load i32, ptr %27, align 4, !tbaa !11
  %29 = add nsw i32 %23, %28
  %30 = load ptr, ptr %3, align 8, !tbaa !5
  %31 = load i64, ptr %5, align 8, !tbaa !9
  %32 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %30, i64 noundef %31) #6
  store i32 %29, ptr %32, align 4, !tbaa !11
  br label %33

33:                                               ; preds = %13
  %34 = load i64, ptr %5, align 8, !tbaa !9
  %35 = add i64 %34, 1
  store i64 %35, ptr %5, align 8, !tbaa !9
  br label %6, !llvm.loop !21

36:                                               ; preds = %12
  ret void
}

; Function Attrs: mustprogress noinline nounwind uwtable
define dso_local void @_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr noundef nonnull align 8 dereferenceable(24) %0, ptr noundef nonnull align 8 dereferenceable(24) %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  store ptr %0, ptr %3, align 8, !tbaa !5
  store ptr %1, ptr %4, align 8, !tbaa !5
  call void @llvm.lifetime.start.p0(i64 8, ptr %5) #6
  %6 = load ptr, ptr %4, align 8, !tbaa !5
  %7 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %6) #6
  store i64 %7, ptr %5, align 8, !tbaa !9
  br label %8

8:                                                ; preds = %13, %2
  %9 = load i64, ptr %5, align 8, !tbaa !9
  %10 = add i64 %9, -1
  store i64 %10, ptr %5, align 8, !tbaa !9
  %11 = icmp ugt i64 %9, 0
  br i1 %11, label %13, label %12

12:                                               ; preds = %8
  call void @llvm.lifetime.end.p0(i64 8, ptr %5) #6
  br label %22

13:                                               ; preds = %8
  %14 = load ptr, ptr %4, align 8, !tbaa !5
  %15 = load i64, ptr %5, align 8, !tbaa !9
  %16 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %14, i64 noundef %15) #6
  %17 = load i32, ptr %16, align 4, !tbaa !11
  %18 = mul nsw i32 %17, 2
  %19 = load ptr, ptr %3, align 8, !tbaa !5
  %20 = load i64, ptr %5, align 8, !tbaa !9
  %21 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %19, i64 noundef %20) #6
  store i32 %18, ptr %21, align 4, !tbaa !11
  br label %8, !llvm.loop !22

22:                                               ; preds = %12
  ret void
}

; Function Attrs: mustprogress noinline nounwind uwtable
define dso_local void @_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr noundef nonnull align 8 dereferenceable(24) %0, ptr noundef nonnull align 8 dereferenceable(24) %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  store ptr %0, ptr %3, align 8, !tbaa !5
  store ptr %1, ptr %4, align 8, !tbaa !5
  call void @llvm.lifetime.start.p0(i64 8, ptr %5) #6
  store i64 0, ptr %5, align 8, !tbaa !9
  br label %6

6:                                                ; preds = %28, %2
  %7 = load i64, ptr %5, align 8, !tbaa !9
  %8 = load ptr, ptr %3, align 8, !tbaa !5
  %9 = call noundef i64 @_ZNKSt3__16vectorIiNS_9allocatorIiEEE4sizeB8fe180100Ev(ptr noundef nonnull align 8 dereferenceable(24) %8) #6
  %10 = icmp ult i64 %7, %9
  br i1 %10, label %12, label %11

11:                                               ; preds = %6
  call void @llvm.lifetime.end.p0(i64 8, ptr %5) #6
  br label %31

12:                                               ; preds = %6
  %13 = load ptr, ptr %4, align 8, !tbaa !5
  %14 = load i64, ptr %5, align 8, !tbaa !9
  %15 = mul i64 2, %14
  %16 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %13, i64 noundef %15) #6
  %17 = load i32, ptr %16, align 4, !tbaa !11
  %18 = load ptr, ptr %4, align 8, !tbaa !5
  %19 = load i64, ptr %5, align 8, !tbaa !9
  %20 = mul i64 2, %19
  %21 = add i64 %20, 1
  %22 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNKSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %18, i64 noundef %21) #6
  %23 = load i32, ptr %22, align 4, !tbaa !11
  %24 = add nsw i32 %17, %23
  %25 = load ptr, ptr %3, align 8, !tbaa !5
  %26 = load i64, ptr %5, align 8, !tbaa !9
  %27 = call noundef nonnull align 4 dereferenceable(4) ptr @_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em(ptr noundef nonnull align 8 dereferenceable(24) %25, i64 noundef %26) #6
  store i32 %24, ptr %27, align 4, !tbaa !11
  br label %28

28:                                               ; preds = %12
  %29 = load i64, ptr %5, align 8, !tbaa !9
  %30 = add i64 %29, 1
  store i64 %30, ptr %5, align 8, !tbaa !9
  br label %6, !llvm.loop !23

31:                                               ; preds = %11
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(none)
declare i64 @llvm.expect.i64(i64, i64) #4

; Function Attrs: cold noreturn nounwind memory(inaccessiblemem: write)
declare void @llvm.trap() #5

attributes #0 = { mustprogress noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" }
attributes #3 = { inlinehint mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" }
attributes #4 = { nocallback nofree nosync nounwind willreturn memory(none) }
attributes #5 = { cold noreturn nounwind memory(inaccessiblemem: write) }
attributes #6 = { nounwind }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2, !3}
!llvm.ident = !{!4}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{!"clang version 18.1.0rc (https://github.com/llvm/llvm-project.git 461274b81d8641eab64d494accddc81d7db8a09e)"}
!5 = !{!6, !6, i64 0}
!6 = !{!"any pointer", !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C++ TBAA"}
!9 = !{!10, !10, i64 0}
!10 = !{!"long", !7, i64 0}
!11 = !{!12, !12, i64 0}
!12 = !{!"int", !7, i64 0}
!13 = distinct !{!13, !14}
!14 = !{!"llvm.loop.mustprogress"}
!15 = !{!16, !6, i64 8}
!16 = !{!"_ZTSNSt3__16vectorIiNS_9allocatorIiEEEE", !6, i64 0, !6, i64 8, !17, i64 16}
!17 = !{!"_ZTSNSt3__117__compressed_pairIPiNS_9allocatorIiEEEE", !18, i64 0}
!18 = !{!"_ZTSNSt3__122__compressed_pair_elemIPiLi0ELb0EEE", !6, i64 0}
!19 = !{!16, !6, i64 0}
!20 = distinct !{!20, !14}
!21 = distinct !{!21, !14}
!22 = distinct !{!22, !14}
!23 = distinct !{!23, !14}
